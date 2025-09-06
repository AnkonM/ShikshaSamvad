"""
Security utilities for authentication system
"""
import re
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from .config import auth_settings
from .models import UserRole

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordValidator:
    """Password validation utility"""
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        """Validate password strength and return (is_valid, errors)"""
        errors = []
        
        if len(password) < auth_settings.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {auth_settings.MIN_PASSWORD_LENGTH} characters long")
        
        if auth_settings.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if auth_settings.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if auth_settings.REQUIRE_NUMBERS and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if auth_settings.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_common_password(password: str) -> bool:
        """Check if password is in common passwords list"""
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', 'qwerty123', 'dragon', 'master'
        }
        return password.lower() in common_passwords

class JWTManager:
    """JWT token management"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.JWT_ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
        """Get user information from JWT token"""
        payload = JWTManager.verify_token(token)
        if payload:
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "role": payload.get("role")
            }
        return None

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username format"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """Validate first/last name format"""
        if len(name.strip()) < 1:
            return False, "Name cannot be empty"
        
        if len(name) > 100:
            return False, "Name must be less than 100 characters"
        
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, ""
    
    @staticmethod
    def validate_student_id(student_id: str) -> tuple[bool, str]:
        """Validate student ID format"""
        if len(student_id) < 3:
            return False, "Student ID must be at least 3 characters long"
        
        if len(student_id) > 20:
            return False, "Student ID must be less than 20 characters"
        
        if not re.match(r'^[A-Za-z0-9_-]+$', student_id):
            return False, "Student ID can only contain letters, numbers, underscores, and hyphens"
        
        return True, ""

class RateLimiter:
    """Rate limiting for authentication endpoints"""
    
    def __init__(self):
        self.attempts = {}  # In production, use Redis or similar
    
    def is_rate_limited(self, identifier: str, max_attempts: int = 5, 
                       window_minutes: int = 15) -> bool:
        """Check if identifier is rate limited"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        # Clean old attempts
        self.attempts[identifier] = [
            attempt_time for attempt_time in self.attempts[identifier]
            if attempt_time > window_start
        ]
        
        return len(self.attempts[identifier]) >= max_attempts
    
    def record_attempt(self, identifier: str) -> None:
        """Record an attempt for rate limiting"""
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        self.attempts[identifier].append(datetime.utcnow())
    
    def reset_attempts(self, identifier: str) -> None:
        """Reset attempts for identifier"""
        if identifier in self.attempts:
            del self.attempts[identifier]

class SecurityHeaders:
    """Security headers for API responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers for API responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'"
        }

class RolePermissions:
    """Role-based permissions management"""
    
    PERMISSIONS = {
        UserRole.STUDENT: [
            "view_own_profile",
            "update_own_profile", 
            "view_own_risk_scores",
            "chat_with_bot",
            "view_own_sessions"
        ],
        UserRole.COUNSELOR: [
            "view_own_profile",
            "update_own_profile",
            "view_assigned_students",
            "view_student_risk_scores",
            "view_chat_logs",
            "moderate_content",
            "view_counselor_dashboard"
        ],
        UserRole.FACULTY: [
            "view_own_profile",
            "update_own_profile",
            "view_class_reports",
            "view_student_alerts",
            "view_faculty_dashboard"
        ],
        UserRole.ADMIN: [
            "view_all_profiles",
            "update_all_profiles",
            "delete_users",
            "manage_roles",
            "view_all_data",
            "system_administration",
            "view_admin_dashboard"
        ]
    }
    
    @staticmethod
    def has_permission(user_role: UserRole, permission: str) -> bool:
        """Check if user role has specific permission"""
        return permission in RolePermissions.PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def get_user_permissions(user_role: UserRole) -> list[str]:
        """Get all permissions for a user role"""
        return RolePermissions.PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def can_access_user_data(current_user_role: UserRole, target_user_role: UserRole) -> bool:
        """Check if current user can access target user's data"""
        if current_user_role == UserRole.ADMIN:
            return True
        
        if current_user_role == UserRole.COUNSELOR and target_user_role == UserRole.STUDENT:
            return True
        
        return current_user_role == target_user_role
