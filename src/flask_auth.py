"""
Flask-Login based authentication system for ShikshaSamvad
"""
from flask import Flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path

class User(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, id, email, role, first_name='', last_name='', student_id=None):
        self.id = id
        self.email = email
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.student_id = student_id
    
    def get_id(self):
        return str(self.id)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_counselor(self):
        return self.role == 'counselor'
    
    def is_faculty(self):
        return self.role == 'faculty'

class AuthManager:
    """Authentication manager using Flask-Login"""
    
    def __init__(self, app=None, db_path="data/processed/shikshasamvaad.db"):
        self.db_path = db_path
        self.login_manager = LoginManager()
        self.login_manager.login_view = 'auth.login'
        self.login_manager.login_message = 'Please log in to access this page.'
        self.login_manager.login_message_category = 'info'
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask-Login with the app"""
        self.login_manager.init_app(app)
        
        @self.login_manager.user_loader
        def load_user(user_id):
            return self.get_user_by_id(user_id)
    
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_user_by_id(self, user_id):
        """Get user by ID for Flask-Login"""
        conn = self.get_db_connection()
        try:
            user_data = conn.execute(
                'SELECT * FROM users WHERE id = ? AND status = "active"',
                (user_id,)
            ).fetchone()
            
            if user_data:
                return User(
                    id=user_data['id'],
                    email=user_data['email'],
                    role=user_data['role'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    student_id=user_data.get('student_id')
                )
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self.get_db_connection()
        try:
            user_data = conn.execute(
                'SELECT * FROM users WHERE email = ? AND status = "active"',
                (email,)
            ).fetchone()
            
            if user_data:
                return User(
                    id=user_data['id'],
                    email=user_data['email'],
                    role=user_data['role'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    student_id=user_data.get('student_id')
                )
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        conn = self.get_db_connection()
        try:
            user_data = conn.execute(
                'SELECT * FROM users WHERE email = ? AND status = "active"',
                (email,)
            ).fetchone()
            
            if user_data and check_password_hash(user_data['password_hash'], password):
                return User(
                    id=user_data['id'],
                    email=user_data['email'],
                    role=user_data['role'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    student_id=user_data.get('student_id')
                )
            return None
        finally:
            conn.close()
    
    def create_user(self, email, password, role='student', first_name='', last_name='', student_id=None):
        """Create a new user"""
        conn = self.get_db_connection()
        try:
            password_hash = generate_password_hash(password)
            cursor = conn.execute(
                '''INSERT INTO users (email, password_hash, role, first_name, last_name, student_id, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (email, password_hash, role, first_name, last_name, student_id, 'active')
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def update_user_password(self, user_id, new_password):
        """Update user password"""
        conn = self.get_db_connection()
        try:
            password_hash = generate_password_hash(new_password)
            conn.execute(
                'UPDATE users SET password_hash = ? WHERE id = ?',
                (password_hash, user_id)
            )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

# Global auth manager instance
auth_manager = AuthManager()

# Convenience functions
def require_auth(f):
    """Decorator to require authentication"""
    return login_required(f)

def require_role(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles and not current_user.is_admin():
                from flask import jsonify
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'Role {current_user.role} not allowed'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current logged in user"""
    return current_user

def is_authenticated():
    """Check if user is authenticated"""
    return current_user.is_authenticated

def is_admin():
    """Check if current user is admin"""
    return current_user.is_authenticated and current_user.is_admin()

def is_student():
    """Check if current user is student"""
    return current_user.is_authenticated and current_user.is_student()

def is_counselor():
    """Check if current user is counselor"""
    return current_user.is_authenticated and current_user.is_counselor()

def is_faculty():
    """Check if current user is faculty"""
    return current_user.is_authenticated and current_user.is_faculty()
