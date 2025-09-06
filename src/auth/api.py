"""
Authentication API endpoints
"""
from flask import Blueprint, request, jsonify, g, make_response
from datetime import datetime, timedelta
from typing import Dict, Any
from .database import AuthDatabase
from .security import (
    PasswordValidator, JWTManager, InputValidator, 
    RolePermissions, RateLimiter
)
from .models import UserRole, UserStatus
from .config import auth_settings
from .middleware import require_auth, require_role, require_permission

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def get_auth_db() -> AuthDatabase:
    """Get authentication database instance"""
    return g.auth_db

@auth_bp.route('/register', methods=['POST'])
@RateLimiter().is_rate_limited
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'error': 'Validation error',
                    'message': f'{field} is required'
                }), 400
        
        # Validate input formats
        if not InputValidator.validate_email(data['email']):
            return jsonify({
                'error': 'Validation error',
                'message': 'Invalid email format'
            }), 400
        
        username_valid, username_error = InputValidator.validate_username(data['username'])
        if not username_valid:
            return jsonify({
                'error': 'Validation error',
                'message': username_error
            }), 400
        
        first_name_valid, first_name_error = InputValidator.validate_name(data['first_name'])
        if not first_name_valid:
            return jsonify({
                'error': 'Validation error',
                'message': first_name_error
            }), 400
        
        last_name_valid, last_name_error = InputValidator.validate_name(data['last_name'])
        if not last_name_valid:
            return jsonify({
                'error': 'Validation error',
                'message': last_name_error
            }), 400
        
        # Validate password strength
        password_valid, password_errors = PasswordValidator.validate_password_strength(data['password'])
        if not password_valid:
            return jsonify({
                'error': 'Validation error',
                'message': 'Password does not meet requirements',
                'details': password_errors
            }), 400
        
        # Check for common password
        if PasswordValidator.is_common_password(data['password']):
            return jsonify({
                'error': 'Validation error',
                'message': 'Password is too common. Please choose a more secure password.'
            }), 400
        
        # Check if user already exists
        auth_db = get_auth_db()
        if auth_db.email_exists(data['email']):
            return jsonify({
                'error': 'User exists',
                'message': 'Email already registered'
            }), 409
        
        if auth_db.username_exists(data['username']):
            return jsonify({
                'error': 'User exists',
                'message': 'Username already taken'
            }), 409
        
        # Determine role (default to student, admin can create other roles)
        role = UserRole.STUDENT
        if 'role' in data and data['role']:
            try:
                role = UserRole(data['role'])
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid role specified'
                }), 400
        
        # Validate student-specific fields
        student_id = data.get('student_id')
        course = data.get('course')
        counselor_id = data.get('counselor_id')
        
        if role == UserRole.STUDENT and student_id:
            if auth_db.student_id_exists(student_id):
                return jsonify({
                    'error': 'User exists',
                    'message': 'Student ID already registered'
                }), 409
            
            student_id_valid, student_id_error = InputValidator.validate_student_id(student_id)
            if not student_id_valid:
                return jsonify({
                    'error': 'Validation error',
                    'message': student_id_error
                }), 400
        
        # Create user
        user = auth_db.create_user(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            student_id=student_id,
            course=course,
            counselor_id=counselor_id
        )
        
        # Generate tokens
        access_token = JWTManager.create_access_token({
            'user_id': user.id,
            'email': user.email,
            'role': user.role.value
        })
        
        refresh_token = JWTManager.create_refresh_token({
            'user_id': user.id,
            'email': user.email
        })
        
        # Create session
        session = auth_db.create_session(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        response_data = {
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
        response = make_response(jsonify(response_data), 201)
        
        # Set secure cookies
        response.set_cookie(
            'access_token', 
            access_token, 
            max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        response.set_cookie(
            'refresh_token',
            refresh_token,
            max_age=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
@RateLimiter().is_rate_limited
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Email and password are required'
            }), 400
        
        # Authenticate user
        auth_db = get_auth_db()
        user = auth_db.authenticate_user(data['email'], data['password'])
        
        if not user:
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid email or password'
            }), 401
        
        if user.status != UserStatus.ACTIVE:
            return jsonify({
                'error': 'Account inactive',
                'message': 'Account is not active. Please contact administrator.'
            }), 401
        
        # Generate tokens
        access_token = JWTManager.create_access_token({
            'user_id': user.id,
            'email': user.email,
            'role': user.role.value
        })
        
        refresh_token = JWTManager.create_refresh_token({
            'user_id': user.id,
            'email': user.email
        })
        
        # Create session
        session = auth_db.create_session(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        response_data = {
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
        response = make_response(jsonify(response_data), 200)
        
        # Set secure cookies
        response.set_cookie(
            'access_token', 
            access_token, 
            max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        response.set_cookie(
            'refresh_token',
            refresh_token,
            max_age=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Login failed',
            'message': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user and invalidate session"""
    try:
        # Get session token from request
        session_token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header.split(' ')[1]
        
        if not session_token:
            session_token = request.cookies.get('access_token')
        
        if session_token:
            auth_db = get_auth_db()
            auth_db.invalidate_session(session_token)
        
        response = make_response(jsonify({
            'message': 'Logout successful'
        }), 200)
        
        # Clear cookies
        response.set_cookie('access_token', '', expires=0)
        response.set_cookie('refresh_token', '', expires=0)
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Logout failed',
            'message': str(e)
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            return jsonify({
                'error': 'Refresh token required',
                'message': 'No refresh token provided'
            }), 401
        
        # Verify refresh token
        payload = JWTManager.verify_token(refresh_token, token_type='refresh')
        if not payload:
            return jsonify({
                'error': 'Invalid refresh token',
                'message': 'Refresh token is invalid or expired'
            }), 401
        
        # Get user
        auth_db = get_auth_db()
        user = auth_db.get_user_by_id(payload.get('user_id'))
        
        if not user or user.status != UserStatus.ACTIVE:
            return jsonify({
                'error': 'User not found',
                'message': 'User account is inactive or not found'
            }), 401
        
        # Generate new access token
        access_token = JWTManager.create_access_token({
            'user_id': user.id,
            'email': user.email,
            'role': user.role.value
        })
        
        response = make_response(jsonify({
            'message': 'Token refreshed successfully',
            'access_token': access_token,
            'expires_in': auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }), 200)
        
        # Set new access token cookie
        response.set_cookie(
            'access_token', 
            access_token, 
            max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Token refresh failed',
            'message': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    try:
        user = g.current_user
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get user info',
            'message': str(e)
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if 'current_password' not in data or 'new_password' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Current password and new password are required'
            }), 400
        
        user = g.current_user
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Current password is incorrect'
            }), 401
        
        # Validate new password
        password_valid, password_errors = PasswordValidator.validate_password_strength(data['new_password'])
        if not password_valid:
            return jsonify({
                'error': 'Validation error',
                'message': 'New password does not meet requirements',
                'details': password_errors
            }), 400
        
        # Check for common password
        if PasswordValidator.is_common_password(data['new_password']):
            return jsonify({
                'error': 'Validation error',
                'message': 'New password is too common. Please choose a more secure password.'
            }), 400
        
        # Change password
        auth_db = get_auth_db()
        success = auth_db.change_password(user.id, data['new_password'])
        
        if success:
            return jsonify({
                'message': 'Password changed successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Password change failed',
                'message': 'Failed to update password'
            }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'Password change failed',
            'message': str(e)
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
@RateLimiter().is_rate_limited
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Email is required'
            }), 400
        
        auth_db = get_auth_db()
        user = auth_db.get_user_by_email(data['email'])
        
        if user:
            # Create password reset token
            reset_token = auth_db.create_password_reset_token(user.id)
            
            # TODO: Send email with reset link
            # For now, just return the token (remove in production)
            return jsonify({
                'message': 'Password reset instructions sent to your email',
                'reset_token': reset_token.token  # Remove in production
            }), 200
        else:
            # Don't reveal if email exists or not
            return jsonify({
                'message': 'If the email exists, password reset instructions have been sent'
            }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Password reset request failed',
            'message': str(e)
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
@RateLimiter().is_rate_limited
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        
        required_fields = ['token', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Validation error',
                    'message': f'{field} is required'
                }), 400
        
        # Validate new password
        password_valid, password_errors = PasswordValidator.validate_password_strength(data['new_password'])
        if not password_valid:
            return jsonify({
                'error': 'Validation error',
                'message': 'New password does not meet requirements',
                'details': password_errors
            }), 400
        
        # Verify reset token
        auth_db = get_auth_db()
        reset_token = auth_db.get_password_reset_token(data['token'])
        
        if not reset_token:
            return jsonify({
                'error': 'Invalid token',
                'message': 'Password reset token is invalid or expired'
            }), 400
        
        # Change password
        success = auth_db.change_password(reset_token.user_id, data['new_password'])
        
        if success:
            # Mark token as used
            auth_db.use_password_reset_token(data['token'])
            
            return jsonify({
                'message': 'Password reset successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Password reset failed',
                'message': 'Failed to update password'
            }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'Password reset failed',
            'message': str(e)
        }), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user email"""
    try:
        data = request.get_json()
        
        if 'token' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Verification token is required'
            }), 400
        
        # TODO: Implement email verification token system
        # For now, this is a placeholder
        
        return jsonify({
            'message': 'Email verification not implemented yet'
        }), 501
        
    except Exception as e:
        return jsonify({
            'error': 'Email verification failed',
            'message': str(e)
        }), 500

@auth_bp.route('/permissions', methods=['GET'])
@require_auth
def get_user_permissions():
    """Get current user permissions"""
    try:
        user_role = g.user_role
        permissions = RolePermissions.get_user_permissions(user_role)
        
        return jsonify({
            'permissions': permissions,
            'role': user_role.value
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get permissions',
            'message': str(e)
        }), 500
