"""
Ultra-simple authentication system for ShikshaSamvad
"""
from flask import Flask, request, jsonify, session, g
from functools import wraps
import hashlib
import sqlite3
from pathlib import Path

class SimpleAuth:
    def __init__(self, app=None, db_path="data/processed/shikshasamvaad.db"):
        self.db_path = db_path
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        app.before_request(self.load_user)
    
    def hash_password(self, password):
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return self.hash_password(password) == hashed
    
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_user(self, email, password, role='student', first_name='', last_name='', student_id=None):
        """Create a new user"""
        conn = self.get_db_connection()
        try:
            password_hash = self.hash_password(password)
            conn.execute(
                '''INSERT INTO users (email, password_hash, role, first_name, last_name, student_id, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (email, password_hash, role, first_name, last_name, student_id, 'active')
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        """Authenticate user and return user data"""
        conn = self.get_db_connection()
        try:
            user = conn.execute(
                'SELECT * FROM users WHERE email = ? AND status = "active"',
                (email,)
            ).fetchone()
            
            if user and self.verify_password(password, user['password_hash']):
                return dict(user)
            return None
        finally:
            conn.close()
    
    def load_user(self):
        """Load user from session"""
        g.user = session.get('user')
    
    def login_user(self, user_data):
        """Login user and set session"""
        session['user'] = {
            'id': user_data['id'],
            'email': user_data['email'],
            'role': user_data['role'],
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'student_id': user_data.get('student_id')
        }
    
    def logout_user(self):
        """Logout user and clear session"""
        session.pop('user', None)
    
    def get_current_user(self):
        """Get current logged in user"""
        return g.user
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user:
                return jsonify({'error': 'Authentication required', 'message': 'Please login first'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def require_role(self, *roles):
        """Decorator to require specific role(s)"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not g.user:
                    return jsonify({'error': 'Authentication required'}), 401
                if g.user['role'] not in roles and g.user['role'] != 'admin':
                    return jsonify({'error': 'Insufficient permissions', 'message': f'Role {g.user["role"]} not allowed'}), 403
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# Global auth instance
auth = SimpleAuth()

# Convenience functions
def require_auth(f):
    return auth.require_auth(f)

def require_role(*roles):
    return auth.require_role(*roles)

def get_current_user():
    return auth.get_current_user()

def is_authenticated():
    return g.user is not None

def is_admin():
    return g.user and g.user['role'] == 'admin'

def is_student():
    return g.user and g.user['role'] == 'student'

def is_counselor():
    return g.user and g.user['role'] == 'counselor'

def is_faculty():
    return g.user and g.user['role'] == 'faculty'
