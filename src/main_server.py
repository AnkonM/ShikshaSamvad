#!/usr/bin/env python3
"""
Main server integrating all ShikshaSamvad services with simple authentication
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.flask_auth import auth_manager, require_auth, require_role, get_current_user
from src.flask_auth_api import auth_bp
from src.chatbot.server import app as chatbot_app
from src.database.sqlite_db import init_db

def create_app():
    """Create the main Flask application"""
    app = Flask(__name__, static_folder='../static', static_url_path='')
    app.secret_key = 'shikshasamvaad-secret-key-change-in-production'
    
    # Enable CORS for frontend
    CORS(app, origins=['http://localhost:3000', 'http://localhost:8501', 'http://localhost:5000'], supports_credentials=True)
    
    # Initialize Flask-Login authentication
    auth_manager.init_app(app)
    
    # Register authentication blueprint
    app.register_blueprint(auth_bp)
    
    # Initialize database
    init_db("sqlite:///data/processed/shikshasamvaad.db", "src/database/schema.sql")
    
    # Create default admin user if it doesn't exist
    create_default_admin(auth_manager)
    
    # Register chatbot routes
    @app.route('/api/chatbot/chat', methods=['POST'])
    @require_auth
    def chat():
        """Chat endpoint with authentication"""
        from src.chatbot.server import chat as chatbot_chat
        return chatbot_chat()
    
    @app.route('/api/chatbot/analyze', methods=['POST'])
    @require_auth
    def analyze():
        """Analyze endpoint with authentication"""
        from src.chatbot.server import analyze as chatbot_analyze
        return chatbot_analyze()
    
    # Dashboard API endpoints
    @app.route('/api/dashboard/risk-data', methods=['GET'])
    @require_auth
    def get_risk_data():
        """Get risk data based on user role"""
        import pandas as pd
        from pathlib import Path
        
        user = get_current_user()
        pred_path = Path("data/processed/risk_predictions.csv")
        
        if pred_path.exists():
            df = pd.read_csv(pred_path)
            
            # Role-based filtering
            if user.role == 'student':
                # Students see only their own data
                df = df[df['student_id'] == user.student_id or '']
            elif user.role == 'counselor':
                # Counselors see assigned students (simplified - all for now)
                pass
            elif user.role == 'faculty':
                # Faculty see class data (simplified - all for now)
                pass
            # Admin sees all data
            
            return jsonify({
                'risk_data': df.to_dict('records'),
                'user_role': user.role
            })
        else:
            return jsonify({
                'error': 'No risk data found',
                'message': 'Generate data and run training/inference first'
            }), 404
    
    @app.route('/api/dashboard/students', methods=['GET'])
    @require_role('counselor', 'faculty', 'admin')
    def get_students():
        """Get students list (counselor/faculty/admin only)"""
        conn = auth_manager.get_db_connection()
        try:
            students = conn.execute(
                'SELECT id, email, first_name, last_name, role, student_id FROM users WHERE role = "student"'
            ).fetchall()
            return jsonify({
                'students': [dict(student) for student in students]
            })
        finally:
            conn.close()
    
    # Risk engine endpoints
    @app.route('/api/risk/predict', methods=['POST'])
    @require_role('counselor', 'admin')
    def predict_risk():
        """Generate risk predictions (counselor/admin only)"""
        try:
            from src.risk_engine.predict import run_inference
            run_inference(
                "data/raw/lms_data.csv",
                "models/risk_engine",
                "data/processed/risk_predictions.csv"
            )
            return jsonify({
                'message': 'Risk predictions generated successfully'
            })
        except Exception as e:
            return jsonify({
                'error': 'Prediction failed',
                'message': str(e)
            }), 500
    
    @app.route('/api/risk/train', methods=['POST'])
    @require_role('admin')
    def train_model():
        """Train risk prediction model (admin only)"""
        try:
            from src.risk_engine.train import train_dummy
            train_dummy(
                "data/raw/lms_data.csv",
                "models/risk_engine"
            )
            return jsonify({
                'message': 'Model training completed successfully'
            })
        except Exception as e:
            return jsonify({
                'error': 'Training failed',
                'message': str(e)
            }), 500
    
    # Serve static files
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'landing-page.html')
    
    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'shikshasamvaad-main',
            'version': '1.0.0'
        })
    
    return app

def create_default_admin(auth_manager):
    """Create default admin user if it doesn't exist"""
    conn = auth_manager.get_db_connection()
    try:
        admin_exists = conn.execute(
            'SELECT id FROM users WHERE email = ?', ('admin@shikshasamvaad.com',)
        ).fetchone()
        
        if not admin_exists:
            auth_manager.create_user(
                email='admin@shikshasamvaad.com',
                password='admin123',
                role='admin',
                first_name='Admin',
                last_name='User'
            )
            print("✅ Default admin user created: admin@shikshasamvaad.com / admin123")
    finally:
        conn.close()

def main():
    """Run the main server"""
    print("🚀 Starting ShikshaSamvad Main Server...")
    print("📊 Authentication: Flask-Login based")
    print("🔗 Services: Chatbot, Dashboard, Risk Engine")
    print("🌐 CORS: Enabled for localhost:3000 and localhost:8501")
    
    app = create_app()
    
    print("\n📋 Available endpoints:")
    print("  POST /api/auth/register - Register new user")
    print("  POST /api/auth/login - Login user")
    print("  POST /api/auth/logout - Logout user")
    print("  GET  /api/auth/me - Get current user")
    print("  POST /api/chatbot/chat - Chat with bot")
    print("  POST /api/chatbot/analyze - Analyze text")
    print("  GET  /api/dashboard/risk-data - Get risk data")
    print("  GET  /api/dashboard/students - Get students list")
    print("  POST /api/risk/predict - Generate predictions")
    print("  POST /api/risk/train - Train model")
    print("  GET  /api/health - Health check")
    
    print("\n🔑 Default admin credentials:")
    print("  Email: admin@shikshasamvaad.com")
    print("  Password: admin123")
    
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()
