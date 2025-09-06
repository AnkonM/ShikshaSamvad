#!/usr/bin/env python3
"""
Setup script for authentication system
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.auth.integration import setup_initial_admin
from src.database.sqlite_db import init_db, get_engine

def setup_authentication():
    """Setup authentication system"""
    print("🔐 Setting up ShikshaSamvad Authentication System...")
    
    # Database URL
    db_url = "sqlite:///data/processed/shikshasamvaad.db"
    
    # Initialize database with auth tables
    print("📊 Initializing database with authentication tables...")
    init_db(db_url, "src/database/schema.sql")
    print("✅ Database initialized successfully")
    
    # Create initial admin user
    print("\n👤 Creating initial admin user...")
    admin_email = input("Enter admin email: ").strip()
    admin_username = input("Enter admin username: ").strip()
    admin_password = input("Enter admin password: ").strip()
    admin_first_name = input("Enter admin first name: ").strip()
    admin_last_name = input("Enter admin last name: ").strip()
    
    if not all([admin_email, admin_username, admin_password, admin_first_name, admin_last_name]):
        print("❌ All fields are required")
        return False
    
    success = setup_initial_admin(
        email=admin_email,
        username=admin_username,
        password=admin_password,
        first_name=admin_first_name,
        last_name=admin_last_name,
        database_url=db_url
    )
    
    if success:
        print("✅ Admin user created successfully")
        print(f"📧 Email: {admin_email}")
        print(f"👤 Username: {admin_username}")
        print("\n🚀 Authentication system is ready!")
        print("\nNext steps:")
        print("1. Start the authentication service: python src/auth/service.py")
        print("2. Test registration: POST /api/auth/register")
        print("3. Test login: POST /api/auth/login")
        print("4. Access protected endpoints with JWT token")
        return True
    else:
        print("❌ Failed to create admin user")
        return False

if __name__ == "__main__":
    setup_authentication()
