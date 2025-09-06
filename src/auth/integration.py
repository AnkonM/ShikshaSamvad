"""
Integration between authentication system and existing services
"""
from flask import Flask, g
from .service import AuthService
from .middleware import require_auth, require_role, require_permission
from .models import UserRole

def integrate_with_chatbot(app: Flask, auth_service: AuthService):
    """Integrate authentication with chatbot service"""
    
    @app.route('/api/chatbot/chat', methods=['POST'])
    @require_auth
    def authenticated_chat():
        """Chat endpoint with authentication"""
        from src.chatbot.server import chat  # Import existing chat function
        return chat()
    
    @app.route('/api/chatbot/analyze', methods=['POST'])
    @require_auth
    def authenticated_analyze():
        """Analyze endpoint with authentication"""
        from src.chatbot.server import analyze  # Import existing analyze function
        return analyze()
    
    @app.route('/api/chatbot/logs', methods=['GET'])
    @require_permission('view_chat_logs')
    def get_chat_logs():
        """Get chat logs (counselor/admin only)"""
        from src.database.sqlite_db import get_engine
        from sqlalchemy import text
        
        # Get user's accessible students
        user = g.current_user
        if user.role == UserRole.ADMIN:
            # Admin can see all logs
            query = "SELECT * FROM chatbot_logs ORDER BY created_at DESC"
        elif user.role == UserRole.COUNSELOR:
            # Counselor can see assigned students' logs
            query = """
                SELECT cl.* FROM chatbot_logs cl
                JOIN users u ON cl.student_id = u.student_id
                WHERE u.counselor_id = :counselor_id
                ORDER BY cl.created_at DESC
            """
        else:
            # Students can only see their own logs
            query = """
                SELECT * FROM chatbot_logs 
                WHERE student_id = :student_id
                ORDER BY created_at DESC
            """
        
        engine = get_engine("sqlite:///data/processed/shikshasamvaad.db")
        with engine.connect() as conn:
            if user.role == UserRole.COUNSELOR:
                result = conn.execute(text(query), {"counselor_id": user.id})
            elif user.role == UserRole.STUDENT:
                result = conn.execute(text(query), {"student_id": user.student_id})
            else:
                result = conn.execute(text(query))
            
            logs = [dict(row) for row in result]
        
        return {"logs": logs}

def integrate_with_dashboard(app: Flask, auth_service: AuthService):
    """Integrate authentication with dashboard service"""
    
    @app.route('/api/dashboard/risk-data', methods=['GET'])
    @require_auth
    def get_risk_data():
        """Get risk data based on user role"""
        from src.database.sqlite_db import get_engine
        from sqlalchemy import text
        
        user = g.current_user
        
        if user.role == UserRole.ADMIN:
            # Admin can see all risk data
            query = "SELECT * FROM risk_scores ORDER BY created_at DESC"
        elif user.role == UserRole.COUNSELOR:
            # Counselor can see assigned students' risk data
            query = """
                SELECT rs.* FROM risk_scores rs
                JOIN users u ON rs.student_id = u.student_id
                WHERE u.counselor_id = :counselor_id
                ORDER BY rs.created_at DESC
            """
        elif user.role == UserRole.FACULTY:
            # Faculty can see class-level data
            query = """
                SELECT rs.* FROM risk_scores rs
                WHERE rs.course = :course
                ORDER BY rs.created_at DESC
            """
        else:
            # Students can only see their own risk data
            query = """
                SELECT * FROM risk_scores 
                WHERE student_id = :student_id
                ORDER BY created_at DESC
            """
        
        engine = get_engine("sqlite:///data/processed/shikshasamvaad.db")
        with engine.connect() as conn:
            if user.role == UserRole.COUNSELOR:
                result = conn.execute(text(query), {"counselor_id": user.id})
            elif user.role == UserRole.FACULTY:
                result = conn.execute(text(query), {"course": user.course})
            elif user.role == UserRole.STUDENT:
                result = conn.execute(text(query), {"student_id": user.student_id})
            else:
                result = conn.execute(text(query))
            
            risk_data = [dict(row) for row in result]
        
        return {"risk_data": risk_data}
    
    @app.route('/api/dashboard/students', methods=['GET'])
    @require_any_role(UserRole.ADMIN, UserRole.COUNSELOR, UserRole.FACULTY)
    def get_students():
        """Get students list based on user role"""
        auth_db = auth_service.get_auth_db()
        
        if g.current_user.role == UserRole.ADMIN:
            students = auth_db.get_users_by_role(UserRole.STUDENT)
        elif g.current_user.role == UserRole.COUNSELOR:
            students = auth_db.get_students_by_counselor(g.current_user.id)
        else:  # Faculty
            students = auth_db.get_users_by_role(UserRole.STUDENT)
            # Filter by course if needed
            students = [s for s in students if s.course == g.current_user.course]
        
        return {"students": [s.to_dict() for s in students]}

def integrate_with_risk_engine(app: Flask, auth_service: AuthService):
    """Integrate authentication with risk engine"""
    
    @app.route('/api/risk/predict', methods=['POST'])
    @require_permission('view_risk_scores')
    def predict_risk():
        """Generate risk predictions (admin/counselor only)"""
        from src.risk_engine.predict import run_inference
        
        # Run risk prediction
        run_inference(
            "data/raw/lms_data.csv",
            "models/risk_engine",
            "data/processed/risk_predictions.csv"
        )
        
        return {"message": "Risk predictions generated successfully"}
    
    @app.route('/api/risk/train', methods=['POST'])
    @require_role(UserRole.ADMIN)
    def train_model():
        """Train risk prediction model (admin only)"""
        from src.risk_engine.train import train_dummy
        
        # Train the model
        train_dummy(
            "data/raw/lms_data.csv",
            "models/risk_engine"
        )
        
        return {"message": "Model training completed successfully"}

def create_authenticated_app(database_url: str = None) -> Flask:
    """Create Flask app with full authentication integration"""
    from src.auth.service import create_auth_app
    
    # Create base auth app
    app = create_auth_app(database_url)
    auth_service = AuthService(app, database_url)
    
    # Integrate with existing services
    integrate_with_chatbot(app, auth_service)
    integrate_with_dashboard(app, auth_service)
    integrate_with_risk_engine(app, auth_service)
    
    # Add health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {"status": "healthy", "service": "shikshasamvad-auth"}
    
    return app

def setup_initial_admin(email: str, username: str, password: str, 
                       first_name: str, last_name: str, 
                       database_url: str = None) -> bool:
    """Setup initial admin user"""
    auth_service = AuthService(database_url=database_url)
    return auth_service.create_admin_user(email, username, password, first_name, last_name)
