#!/usr/bin/env python3
"""
Start script for ShikshaSamvad with Flask-Login integration
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def start_flask_login_system():
    """Start the complete ShikshaSamvad system with Flask-Login"""
    print("🚀 Starting ShikshaSamvad with Flask-Login Integration...")
    print("=" * 60)
    
    # Check if database exists
    db_path = Path("data/processed/shikshasamvaad.db")
    if not db_path.exists():
        print("📊 Database not found. Setting up system...")
        import subprocess
        import os
        
        # Set PYTHONPATH for subprocess calls
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())
        
        subprocess.run([sys.executable, "scripts/setup_simple_auth.py"], check=True, env=env)
        print("✅ System setup completed!")
    
    print("\n🔐 Flask-Login Authentication Features:")
    print("  ✅ Flask-Login session management")
    print("  ✅ Secure password hashing with Werkzeug")
    print("  ✅ Remember me functionality")
    print("  ✅ Role-based access control")
    print("  ✅ Automatic session handling")
    print("  ✅ CSRF protection via sessions")
    
    print("\n🌐 Frontend Integration Features:")
    print("  ✅ HTML5 frontend with Tailwind CSS")
    print("  ✅ Role-based dashboard (Student, Counselor, Faculty, Admin)")
    print("  ✅ Real-time AI chat interface")
    print("  ✅ Risk assessment tables")
    print("  ✅ Responsive design for all devices")
    print("  ✅ Flask-Login session authentication")
    
    print("\n🔗 Available URLs:")
    print("  🏠 Landing Page: http://localhost:5000")
    print("  🔐 Login: http://localhost:5000/login.html")
    print("  📝 Signup: http://localhost:5000/signup.html")
    print("  📊 Dashboard: http://localhost:5000/dashboard.html")
    print("  🔧 API Health: http://localhost:5000/api/health")
    
    print("\n🔑 Default Admin Credentials:")
    print("  Email: admin@shikshasamvaad.com")
    print("  Password: admin123")
    print("  Role: admin")
    
    print("\n📱 Frontend Features by Role:")
    print("  👨‍🎓 Student: AI chat, personal data, progress tracking")
    print("  👩‍⚕️ Counselor: Risk assessments, student management")
    print("  👨‍🏫 Faculty: Class reports, student alerts, analytics")
    print("  👨‍💼 Admin: System stats, user management, monitoring")
    
    print("\n🔧 Flask-Login Benefits:")
    print("  ✅ Industry-standard authentication")
    print("  ✅ Automatic session management")
    print("  ✅ Secure password handling")
    print("  ✅ Easy role-based permissions")
    print("  ✅ Remember me functionality")
    print("  ✅ CSRF protection")
    
    print("\n🚀 Starting server...")
    print("=" * 60)
    
    # Start the main server
    from src.main_server import main
    main()

if __name__ == "__main__":
    start_flask_login_system()
