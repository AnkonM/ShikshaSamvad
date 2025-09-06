"""
Database operations for authentication system
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .models import User, UserSession, PasswordResetToken, UserRole, UserStatus
from .config import auth_settings
import secrets
import string

class AuthDatabase:
    """Database operations for authentication"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # User CRUD Operations
    def create_user(self, email: str, username: str, password: str, 
                   first_name: str, last_name: str, role: UserRole = UserRole.STUDENT,
                   student_id: Optional[str] = None, course: Optional[str] = None,
                   counselor_id: Optional[int] = None) -> User:
        """Create a new user"""
        user = User(
            email=email.lower().strip(),
            username=username.lower().strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role,
            student_id=student_id,
            course=course,
            counselor_id=counselor_id
        )
        user.set_password(password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email.lower().strip()).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username.lower().strip()).first()
    
    def get_user_by_student_id(self, student_id: str) -> Optional[User]:
        """Get user by student ID"""
        return self.db.query(User).filter(User.student_id == student_id).first()
    
    def update_user(self, user: User) -> User:
        """Update user"""
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by setting status to inactive)"""
        user = self.get_user_by_id(user_id)
        if user:
            user.status = UserStatus.INACTIVE
            self.update_user(user)
            return True
        return False
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users by role"""
        return self.db.query(User).filter(User.role == role).all()
    
    def get_students_by_counselor(self, counselor_id: int) -> List[User]:
        """Get students assigned to a counselor"""
        return self.db.query(User).filter(
            and_(
                User.role == UserRole.STUDENT,
                User.counselor_id == counselor_id
            )
        ).all()
    
    # Authentication Operations
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        # Check if account is locked
        if user.is_locked():
            return None
        
        # Check password
        if user.check_password(password):
            user.reset_failed_login()
            self.update_user(user)
            return user
        else:
            user.increment_failed_login()
            self.update_user(user)
            return None
    
    def verify_email(self, user_id: int) -> bool:
        """Verify user email"""
        user = self.get_user_by_id(user_id)
        if user:
            user.email_verified_at = datetime.utcnow()
            user.status = UserStatus.ACTIVE
            self.update_user(user)
            return True
        return False
    
    # Session Management
    def create_session(self, user_id: int, ip_address: str = None, 
                      user_agent: str = None) -> UserSession:
        """Create a new user session"""
        # Generate tokens
        session_token = self._generate_token(32)
        refresh_token = self._generate_token(32)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session_by_token(self, session_token: str) -> Optional[UserSession]:
        """Get session by token"""
        return self.db.query(UserSession).filter(
            and_(
                UserSession.session_token == session_token,
                UserSession.is_active == True
            )
        ).first()
    
    def get_session_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """Get session by refresh token"""
        return self.db.query(UserSession).filter(
            and_(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            )
        ).first()
    
    def refresh_session(self, session: UserSession) -> UserSession:
        """Refresh session tokens"""
        session.session_token = self._generate_token(32)
        session.refresh_token = self._generate_token(32)
        session.expires_at = datetime.utcnow() + timedelta(days=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        session.refresh()
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session"""
        session = self.get_session_by_token(session_token)
        if session:
            session.is_active = False
            self.db.commit()
            return True
        return False
    
    def invalidate_user_sessions(self, user_id: int) -> int:
        """Invalidate all sessions for a user"""
        sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).all()
        
        for session in sessions:
            session.is_active = False
        
        self.db.commit()
        return len(sessions)
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            session.is_active = False
        
        self.db.commit()
        return len(expired_sessions)
    
    # Password Reset
    def create_password_reset_token(self, user_id: int) -> PasswordResetToken:
        """Create password reset token"""
        token = self._generate_token(32)
        expires_at = datetime.utcnow() + timedelta(hours=auth_settings.PASSWORD_RESET_EXPIRE_HOURS)
        
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        self.db.add(reset_token)
        self.db.commit()
        self.db.refresh(reset_token)
        return reset_token
    
    def get_password_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get password reset token"""
        return self.db.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        ).first()
    
    def use_password_reset_token(self, token: str) -> bool:
        """Mark password reset token as used"""
        reset_token = self.get_password_reset_token(token)
        if reset_token:
            reset_token.used = True
            self.db.commit()
            return True
        return False
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        user = self.get_user_by_id(user_id)
        if user:
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            self.update_user(user)
            return True
        return False
    
    # Utility Methods
    def _generate_token(self, length: int = 32) -> str:
        """Generate random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.get_user_by_email(email) is not None
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        return self.get_user_by_username(username) is not None
    
    def student_id_exists(self, student_id: str) -> bool:
        """Check if student ID already exists"""
        return self.get_user_by_student_id(student_id) is not None
