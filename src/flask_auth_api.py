"""
Flask-Login API endpoints for authentication
"""
from flask import Blueprint, request, jsonify, session
from .flask_auth import auth_manager, login_user, logout_user, current_user

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'error': 'Validation error',
                    'message': f'{field} is required'
                }), 400
        
        # Check if user already exists
        existing_user = auth_manager.get_user_by_email(data['email'])
        if existing_user:
            return jsonify({
                'error': 'User exists',
                'message': 'Email already registered'
            }), 409
        
        # Create user (derive username from email if not provided)
        user_id = auth_manager.create_user(
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'student'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            student_id=data.get('student_id'),
            username=data.get('username')
        )
        
        if user_id:
            return jsonify({
                'message': 'User registered successfully',
                'user_id': user_id
            }), 201
        else:
            return jsonify({
                'error': 'Registration failed',
                'message': 'Failed to create user'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Email and password are required'
            }), 400
        
        # Authenticate user
        user = auth_manager.authenticate_user(data['email'], data['password'])
        
        if user:
            login_user(user, remember=data.get('remember', False))
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'student_id': user.student_id
                }
            }), 200
        else:
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'error': 'Login failed',
            'message': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        logout_user()
        return jsonify({
            'message': 'Logout successful'
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Logout failed',
            'message': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    try:
        if current_user.is_authenticated:
            return jsonify({
                'user': {
                    'id': current_user.id,
                    'email': current_user.email,
                    'role': current_user.role,
                    'first_name': current_user.first_name,
                    'last_name': current_user.last_name,
                    'student_id': current_user.student_id
                }
            }), 200
        else:
            return jsonify({
                'error': 'Not authenticated',
                'message': 'User not logged in'
            }), 401
    except Exception as e:
        return jsonify({
            'error': 'Failed to get user info',
            'message': str(e)
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        if not current_user.is_authenticated:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please login first'
            }), 401
        
        data = request.get_json()
        
        if 'current_password' not in data or 'new_password' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Current password and new password are required'
            }), 400
        
        # Verify current password
        user = auth_manager.authenticate_user(current_user.email, data['current_password'])
        if not user:
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Current password is incorrect'
            }), 401
        
        # Update password
        success = auth_manager.update_user_password(current_user.id, data['new_password'])
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

@auth_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'flask-auth',
        'authenticated': current_user.is_authenticated
    }), 200
