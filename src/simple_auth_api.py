"""
Simple authentication API endpoints
"""
from flask import Blueprint, request, jsonify
from .simple_auth import auth

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
        conn = auth.get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (data['email'],)
        ).fetchone()
        conn.close()
        
        if existing_user:
            return jsonify({
                'error': 'User exists',
                'message': 'Email already registered'
            }), 409
        
        # Create user
        success = auth.create_user(
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'student'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            student_id=data.get('student_id')
        )
        
        if success:
            return jsonify({
                'message': 'User registered successfully'
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
        user = auth.authenticate_user(data['email'], data['password'])
        
        if user:
            auth.login_user(user)
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'role': user['role'],
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', ''),
                    'student_id': user.get('student_id')
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
        auth.logout_user()
        return jsonify({
            'message': 'Logout successful'
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Logout failed',
            'message': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
@auth.require_auth
def get_current_user():
    """Get current user information"""
    try:
        user = auth.get_current_user()
        return jsonify({
            'user': user
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to get user info',
            'message': str(e)
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@auth.require_auth
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if 'current_password' not in data or 'new_password' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Current password and new password are required'
            }), 400
        
        user = auth.get_current_user()
        
        # Verify current password
        conn = auth.get_db_connection()
        user_data = conn.execute(
            'SELECT password_hash FROM users WHERE id = ?', (user['id'],)
        ).fetchone()
        conn.close()
        
        if not auth.verify_password(data['current_password'], user_data['password_hash']):
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Current password is incorrect'
            }), 401
        
        # Update password
        conn = auth.get_db_connection()
        new_password_hash = auth.hash_password(data['new_password'])
        conn.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (new_password_hash, user['id'])
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
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
        'service': 'simple-auth'
    }), 200
