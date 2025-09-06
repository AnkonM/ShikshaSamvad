"""
Authentication middleware and decorators
"""
from functools import wraps
from typing import Optional, Callable, Any
from flask import request, jsonify, g
from .security import JWTManager, RolePermissions
from .models import UserRole
from .database import AuthDatabase
from .config import auth_settings

def get_auth_db() -> AuthDatabase:
    """Get authentication database instance"""
    # This would be injected from your main app
    # For now, we'll assume it's available in g
    return g.auth_db

def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Get token from cookies as fallback
        if not token:
            token = request.cookies.get('access_token')
        
        if not token:
            return jsonify({
                'error': 'Authentication required',
                'message': 'No valid token provided'
            }), 401
        
        # Verify token
        payload = JWTManager.verify_token(token)
        if not payload:
            return jsonify({
                'error': 'Invalid token',
                'message': 'Token is invalid or expired'
            }), 401
        
        # Get user from database
        auth_db = get_auth_db()
        user = auth_db.get_user_by_id(payload.get('user_id'))
        
        if not user or user.status != 'active':
            return jsonify({
                'error': 'User not found',
                'message': 'User account is inactive or not found'
            }), 401
        
        # Add user to request context
        g.current_user = user
        g.user_id = user.id
        g.user_role = user.role
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role: UserRole) -> Callable:
    """Decorator to require specific role"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if g.user_role != required_role and g.user_role != UserRole.ADMIN:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'Role {required_role.value} required'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_permission(permission: str) -> Callable:
    """Decorator to require specific permission"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if not RolePermissions.has_permission(g.user_role, permission):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'Permission {permission} required'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_any_role(*roles: UserRole) -> Callable:
    """Decorator to require any of the specified roles"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if g.user_role not in roles and g.user_role != UserRole.ADMIN:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'One of roles {[r.value for r in roles]} required'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def optional_auth(f: Callable) -> Callable:
    """Decorator for optional authentication (user may or may not be logged in)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Get token from cookies as fallback
        if not token:
            token = request.cookies.get('access_token')
        
        if token:
            # Verify token
            payload = JWTManager.verify_token(token)
            if payload:
                # Get user from database
                auth_db = get_auth_db()
                user = auth_db.get_user_by_id(payload.get('user_id'))
                
                if user and user.status == 'active':
                    g.current_user = user
                    g.user_id = user.id
                    g.user_role = user.role
                else:
                    g.current_user = None
                    g.user_id = None
                    g.user_role = None
            else:
                g.current_user = None
                g.user_id = None
                g.user_role = None
        else:
            g.current_user = None
            g.user_id = None
            g.user_role = None
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_user_access(target_user_id: int) -> bool:
    """Validate if current user can access target user's data"""
    if not hasattr(g, 'current_user') or not g.current_user:
        return False
    
    # Admin can access all users
    if g.user_role == UserRole.ADMIN:
        return True
    
    # Users can access their own data
    if g.user_id == target_user_id:
        return True
    
    # Counselors can access their assigned students
    if g.user_role == UserRole.COUNSELOR:
        auth_db = get_auth_db()
        target_user = auth_db.get_user_by_id(target_user_id)
        if target_user and target_user.counselor_id == g.user_id:
            return True
    
    return False

def require_user_access(f: Callable) -> Callable:
    """Decorator to require access to specific user data"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        # Extract target user ID from route parameters
        target_user_id = request.view_args.get('user_id')
        if not target_user_id:
            return jsonify({
                'error': 'Invalid request',
                'message': 'User ID not specified'
            }), 400
        
        try:
            target_user_id = int(target_user_id)
        except ValueError:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Invalid user ID format'
            }), 400
        
        if not validate_user_access(target_user_id):
            return jsonify({
                'error': 'Access denied',
                'message': 'You do not have permission to access this user\'s data'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit(max_attempts: int = 5, window_minutes: int = 15) -> Callable:
    """Decorator for rate limiting"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from .security import RateLimiter
            
            # Get client identifier (IP address)
            client_ip = request.remote_addr
            if not client_ip:
                client_ip = 'unknown'
            
            rate_limiter = RateLimiter()
            
            if rate_limiter.is_rate_limited(client_ip, max_attempts, window_minutes):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many attempts. Please try again in {window_minutes} minutes.'
                }), 429
            
            # Record the attempt
            rate_limiter.record_attempt(client_ip)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def add_security_headers(response):
    """Add security headers to response"""
    from .security import SecurityHeaders
    
    headers = SecurityHeaders.get_security_headers()
    for header, value in headers.items():
        response.headers[header] = value
    
    return response

def get_current_user() -> Optional[dict]:
    """Get current user information"""
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user.to_dict(include_sensitive=True)
    return None

def get_current_user_id() -> Optional[int]:
    """Get current user ID"""
    return getattr(g, 'user_id', None)

def get_current_user_role() -> Optional[UserRole]:
    """Get current user role"""
    return getattr(g, 'user_role', None)

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return hasattr(g, 'current_user') and g.current_user is not None

def is_admin() -> bool:
    """Check if current user is admin"""
    return get_current_user_role() == UserRole.ADMIN

def is_counselor() -> bool:
    """Check if current user is counselor"""
    return get_current_user_role() == UserRole.COUNSELOR

def is_student() -> bool:
    """Check if current user is student"""
    return get_current_user_role() == UserRole.STUDENT

def is_faculty() -> bool:
    """Check if current user is faculty"""
    return get_current_user_role() == UserRole.FACULTY
