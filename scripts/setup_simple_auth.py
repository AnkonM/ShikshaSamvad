#!/usr/bin/env python3
"""
Setup script for simple authentication system
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def setup_simple_auth():
    """Setup simple authentication system"""
    print("🔐 Setting up Simple Authentication System...")
    
    # Create necessary directories
    data_dir = Path("data/processed")
    data_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Created data directories")
    
    # Initialize database
    print("📊 Initializing database...")
    from src.database.sqlite_db import init_db
    init_db("sqlite:///data/processed/shikshasamvaad.db", "src/database/schema.sql")
    print("✅ Database initialized")
    
    # Generate sample data
    print("📈 Generating sample data...")
    from scripts.generate_lms_data import main as generate_data
    generate_data()
    print("✅ Sample data generated")
    
    # Ingest data
    print("💾 Ingesting data...")
    from scripts.ingest_lms_data import main as ingest_data
    ingest_data()
    print("✅ Data ingested")
    
    print("\n🎉 Simple authentication system is ready!")
    print("\n📋 Next steps:")
    print("1. Start the main server: python src/main_server.py")
    print("2. Start the dashboard: streamlit run src/dashboard/streamlit_app.py")
    print("3. Test the API endpoints")
    
    print("\n🔑 Default admin credentials:")
    print("  Email: admin@shikshasamvaad.com")
    print("  Password: admin123")
    
    print("\n🌐 Services will be available at:")
    print("  Main API: http://localhost:5000")
    print("  Dashboard: http://localhost:8501")

if __name__ == "__main__":
    setup_simple_auth()
