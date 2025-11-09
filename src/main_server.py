#!/usr/bin/env python3
"""
Main server integrating all ShikshaSamvad services with simple authentication
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path
import json

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
    app.secret_key = 'shikshasamvad-secret-key-change-in-production'
    
    # Enable CORS for frontend
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5000'], supports_credentials=True)
    
    # Initialize Flask-Login authentication
    auth_manager.init_app(app)
    
    # Register authentication blueprint
    app.register_blueprint(auth_bp)
    
    # Initialize database
    init_db("sqlite:///data/processed/shikshasamvad.db", "src/database/schema.sql")
    
    # Create default admin user if it doesn't exist
    create_default_admin(auth_manager)
    
    # DEBUG: Print routes after auth setup
    print("\n=== Routes after auth setup ===")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")
    print("=" * 40)
    
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
    
    # DEBUG: Print routes after chatbot setup
    print("\n=== Routes after chatbot setup ===")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")
    print("=" * 40)
    
    # Dashboard API endpoints
    @app.route('/api/dashboard/risk-data', methods=['GET'])
    @require_auth
    def get_risk_data():
        """Get risk data based on user role"""
        import pandas as pd

        user = get_current_user()
        conn = auth_manager.get_db_connection()
        try:
            df = pd.read_sql_query('SELECT student_id, course, dropout_risk, risk_ci_lower, risk_ci_upper FROM risk_scores', conn)
        finally:
            conn.close()

        if df.empty:
            return jsonify({
                'error': 'No risk data found',
                'message': 'Generate data and run training/inference first'
            }), 404

        if user.role == 'student' and user.student_id:
            df = df[df['student_id'] == user.student_id]
        # counselors/faculty get full set (future: filter assigned)

        return jsonify({
            'risk_data': df.to_dict('records'),
            'user_role': user.role
        })

    @app.route('/api/dashboard/performance-summary', methods=['GET'])
    @require_auth
    def get_performance_summary():
        """Return attendance and assessment summary for charts"""
        import pandas as pd

        user = get_current_user()
        conn = auth_manager.get_db_connection()
        try:
            assessments_df = pd.read_sql_query('SELECT student_id, course_code, score, max_score FROM assessments', conn)
            attendance_df = pd.read_sql_query('SELECT student_id, course_code, present FROM attendance_records', conn)
            courses_df = pd.read_sql_query('SELECT course_code, name FROM courses', conn)
        finally:
            conn.close()

        if assessments_df.empty:
            return jsonify({'summary': []})

        if user.role == 'student' and user.student_id:
            assessments_df = assessments_df[assessments_df['student_id'] == user.student_id]
            attendance_df = attendance_df[attendance_df['student_id'] == user.student_id]

        summary = []
        course_codes = sorted(assessments_df['course_code'].unique())
        for code in course_codes:
            assess_subset = assessments_df[assessments_df['course_code'] == code]
            attendance_subset = attendance_df[attendance_df['course_code'] == code]
            if assess_subset.empty:
                continue
            avg_score = round(assess_subset['score'].mean(), 2)
            max_score = assess_subset['max_score'].mean() if 'max_score' in assess_subset else 100
            attendance_pct = None
            if not attendance_subset.empty:
                attendance_pct = round(attendance_subset['present'].astype(float).mean() * 100, 2)
            course_name = courses_df[courses_df['course_code'] == code]['name'].iloc[0] if not courses_df.empty else code
            summary.append({
                'course_code': code,
                'course_name': course_name,
                'avg_score': avg_score,
                'max_score': max_score,
                'attendance_pct': attendance_pct
            })

        return jsonify({'summary': summary})

    @app.route('/api/dashboard/assessments', methods=['GET'])
    @require_auth
    def get_assessment_trend():
        """Return chronological assessment scores for a student/course"""
        import pandas as pd

        user = get_current_user()
        student_id = request.args.get('student_id')
        course_code = request.args.get('course_code')

        if user.role == 'student' and user.student_id:
            student_id = user.student_id

        if not student_id or not course_code:
            return jsonify({'assessments': []})

        conn = auth_manager.get_db_connection()
        try:
            query = 'SELECT assessment_type, assessment_name, score, max_score, submitted_at FROM assessments WHERE student_id = ? AND course_code = ? ORDER BY submitted_at'
            rows = conn.execute(query, (student_id, course_code)).fetchall()
        finally:
            conn.close()

        assessments = []
        for row in rows:
            item = dict(row)
            assessments.append({
                'assessment_type': item['assessment_type'],
                'assessment_name': item['assessment_name'],
                'score': item['score'],
                'max_score': item['max_score'],
                'submitted_at': item['submitted_at']
            })

        return jsonify({'assessments': assessments})

    @app.route('/api/dashboard/course-attributes', methods=['GET'])
    @require_auth
    def get_course_attributes():
        """Return attribute weights for a course"""
        course_code = request.args.get('course_code')
        if not course_code:
            return jsonify({'attributes': {}})

        conn = auth_manager.get_db_connection()
        try:
            row = conn.execute('SELECT attributes_json FROM courses WHERE course_code = ?', (course_code,)).fetchone()
        finally:
            conn.close()

        if not row or not row['attributes_json']:
            return jsonify({'attributes': {}})

        try:
            attrs = json.loads(row['attributes_json'])
        except (TypeError, json.JSONDecodeError):
            attrs = {}

        return jsonify({'attributes': attrs})
    
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
    
    # DEBUG: Print routes before risk endpoints
    print("\n=== Routes before risk endpoints ===")
    for rule in app.url_map.iter_rules():
        if 'risk' in rule.rule:
            print(f"  EXISTING RISK ROUTE: {rule.methods} {rule.rule} -> {rule.endpoint}")
    print("=" * 40)
    
    # Risk engine endpoints
    print("About to register /api/risk/predict route...")
    
    @app.route('/api/risk/predict', methods=['POST'], endpoint='predict_risk_main')
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
    
    print("Successfully registered /api/risk/predict route!")
    
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
            'service': 'shikshasamvad-main',
            'version': '1.0.0'
        })
    
    # DEBUG: Print all final routes
    print("\n=== All final routes ===")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")
    print("=" * 40)
    
    return app

def create_default_admin(auth_manager):
    """Create default admin user if it doesn't exist"""
    conn = auth_manager.get_db_connection()
    try:
        admin_exists = conn.execute(
            'SELECT id FROM users WHERE email = ?', ('admin@shikshasamvad.com',)
        ).fetchone()
        
        if not admin_exists:
            auth_manager.create_user(
                email='admin@shikshasamvad.com',
                password='admin123',
                role='admin',
                first_name='Admin',
                last_name='User',
                username='admin'
            )
            print("✅ Default admin user created: admin@shikshasamvad.com / admin123")
    finally:
        conn.close()

def main():
    """Run the main server"""
    print("🚀 Starting ShikshaSamvad Main Server...")
    print("📊 Authentication: Flask-Login based")
    print("🔗 Services: Chatbot, Dashboard, Risk Engine")
    print("🌐 CORS: Enabled for localhost:3000 and localhost:5000")
    
    app = create_app()
    
    print("\n📋 Available endpoints:")
    print("  POST /api/auth/register - Register new user")
    print("  POST /api/auth/login - Login user")
    print("  POST /api/auth/logout - Logout user")
    print("  GET  /api/auth/me - Get current user")
    print("  POST /api/chatbot/chat - Chat with bot")
    print("  POST /api/chatbot/analyze - Analyze text")
    print("  GET  /api/dashboard/risk-data - Get risk data")
    print("  GET  /api/dashboard/performance-summary - Performance data")
    print("  GET  /api/dashboard/assessments - Assessment trend")
    print("  GET  /api/dashboard/course-attributes - Course attributes")
    print("  GET  /api/dashboard/students - Get students list")
    print("  POST /api/risk/predict - Generate predictions")
    print("  POST /api/risk/train - Train model")
    print("  GET  /api/health - Health check")
    
    print("\n🔑 Default admin credentials:")
    print("  Email: admin@shikshasamvad.com")
    print("  Password: admin123")
    
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()
