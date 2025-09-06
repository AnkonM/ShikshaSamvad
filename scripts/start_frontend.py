#!/usr/bin/env python3
"""
Start script for ShikshaSamvad with frontend integration
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def start_frontend_system():
    """Start the complete ShikshaSamvad system with frontend"""
    print("🚀 Starting ShikshaSamvad Frontend System...")
    print("=" * 50)
    
    # Check if database exists
    db_path = Path("data/processed/shikshasamvaad.db")
    if not db_path.exists():
        print("📊 Database not found. Setting up system...")
        import subprocess
        import sys
        subprocess.run([sys.executable, "scripts/setup_simple_auth.py"], check=True)
        print("✅ System setup completed!")
    
    print("\n🌐 Frontend Integration Features:")
    print("  ✅ HTML5 frontend with Tailwind CSS")
    print("  ✅ Role-based dashboard (Student, Counselor, Faculty, Admin)")
    print("  ✅ Real-time AI chat interface")
    print("  ✅ Risk assessment tables")
    print("  ✅ Responsive design for all devices")
    print("  ✅ Session-based authentication")
    
    print("\n🔗 Available URLs:")
    print("  🏠 Landing Page: http://localhost:5000")
    print("  🔐 Login: http://localhost:5000/login.html")
    print("  📝 Signup: http://localhost:5000/signup.html")
    print("  📊 Dashboard: http://localhost:5000/dashboard.html")
    print("  🔧 API Health: http://localhost:5000/api/health")
    
    print("\n🔑 Default Admin Credentials:")
    print("  Email: admin@shikshasamvaad.com")
    print("  Password: admin123")
    
    print("\n📱 Frontend Features by Role:")
    print("  👨‍🎓 Student: AI chat, personal data, progress tracking")
    print("  👩‍⚕️ Counselor: Risk assessments, student management")
    print("  👨‍🏫 Faculty: Class reports, student alerts, analytics")
    print("  👨‍💼 Admin: System stats, user management, monitoring")
    
    print("\n🚀 Starting server...")
    print("=" * 50)
    
    # Start the main server
    from src.main_server import main
    main()

if __name__ == "__main__":
    start_frontend_system()
