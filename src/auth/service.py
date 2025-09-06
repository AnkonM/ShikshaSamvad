"""
Authentication service - main entry point
"""
from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .database import AuthDatabase
from .api import auth_bp
from .config import auth_settings
from .middleware import add_security_headers

class AuthService:
    """Main authentication service"""
    
    def __init__(self, app: Flask = None, database_url: str = None):
        self.app = app
        self.database_url = database_url or "sqlite:///data/processed/auth.db"
        self.engine = None
        self.SessionLocal = None
        self.auth_db = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize authentication service with Flask app"""
        self.app = app
        
        # Configure CORS
        CORS(app, 
             origins=auth_settings.ALLOWED_ORIGINS,
             supports_credentials=True,
             allow_headers=["Content-Type", "Authorization"],
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        
        # Setup database
        self.setup_database()
        
        # Register blueprints
        app.register_blueprint(auth_bp)
        
        # Add security headers
        app.after_request(add_security_headers)
        
        # Add auth_db to app context
        @app.before_request
        def before_request():
            from flask import g
            g.auth_db = self.get_auth_db()
    
    def setup_database(self):
        """Setup authentication database"""
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_auth_db(self) -> AuthDatabase:
        """Get authentication database instance"""
        if not self.SessionLocal:
            self.setup_database()
        
        session = self.SessionLocal()
        return AuthDatabase(session)
    
    def create_admin_user(self, email: str, username: str, password: str, 
                         first_name: str, last_name: str) -> bool:
        """Create initial admin user"""
        try:
            auth_db = self.get_auth_db()
            
            # Check if admin already exists
            existing_admin = auth_db.get_users_by_role("admin")
            if existing_admin:
                return False
            
            # Create admin user
            admin_user = auth_db.create_user(
                email=email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role="admin"
            )
            
            # Activate admin account
            admin_user.status = "active"
            admin_user.email_verified_at = auth_db.db.query(auth_db.db.query().filter().first()).first()
            auth_db.update_user(admin_user)
            
            return True
            
        except Exception as e:
            print(f"Error creating admin user: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            auth_db = self.get_auth_db()
            return auth_db.cleanup_expired_sessions()
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0

def create_auth_app(database_url: str = None) -> Flask:
    """Create Flask app with authentication"""
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = auth_settings.SECRET_KEY
    app.config['JSON_SORT_KEYS'] = False
    
    # Initialize auth service
    auth_service = AuthService(app, database_url)
    
    return app

# Global auth service instance
auth_service = None

def init_auth_service(database_url: str = None):
    """Initialize global auth service"""
    global auth_service
    auth_service = AuthService(database_url=database_url)
    return auth_service

def get_auth_service() -> AuthService:
    """Get global auth service instance"""
    global auth_service
    if not auth_service:
        auth_service = AuthService()
    return auth_service
