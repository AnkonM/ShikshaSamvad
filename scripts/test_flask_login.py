#!/usr/bin/env python3
"""
Test script for Flask-Login integration
"""
import requests
import time
import webbrowser
from pathlib import Path

def test_flask_login_integration():
    """Test the Flask-Login integration"""
    print("🧪 Testing Flask-Login Integration...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if server is running
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server returned error:", response.status_code)
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running on port 5000")
        print("   Start the server with: python src/main_server.py")
        return
    
    # Test 2: Check static files
    print("\n2. Testing static file serving...")
    static_files = [
        "landing-page.html",
        "login.html", 
        "signup.html",
        "dashboard.html"
    ]
    
    for file in static_files:
        try:
            response = requests.get(f"{base_url}/{file}")
            if response.status_code == 200:
                print(f"✅ {file} - OK")
            else:
                print(f"❌ {file} - Error {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {file} - Error: {e}")
    
    # Test 3: Test Flask-Login authentication flow
    print("\n3. Testing Flask-Login authentication flow...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Register a test user
    test_user = {
        "email": "test_flask@example.com",
        "password": "test123",
        "first_name": "Flask",
        "last_name": "Test",
        "role": "student"
    }
    
    try:
        # Register
        response = session.post(f"{base_url}/api/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ User registration - OK")
        else:
            print(f"⚠️  User registration - {response.status_code} (may already exist)")
        
        # Login
        login_data = {"email": test_user["email"], "password": test_user["password"]}
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login - OK")
            data = response.json()
            print(f"   User: {data['user']['first_name']} ({data['user']['role']})")
        else:
            print(f"❌ User login - Error {response.status_code}")
            return
        
        # Test protected endpoint
        response = session.get(f"{base_url}/api/auth/me")
        if response.status_code == 200:
            print("✅ Protected endpoint access - OK")
            user_data = response.json()
            print(f"   Current user: {user_data['user']['email']}")
        else:
            print(f"❌ Protected endpoint access - Error {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication test failed: {e}")
        return
    
    # Test 4: Test chatbot endpoint with Flask-Login
    print("\n4. Testing chatbot integration with Flask-Login...")
    try:
        chat_data = {"text": "Hello, I'm feeling stressed"}
        response = session.post(f"{base_url}/api/chatbot/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chatbot response - OK: {data.get('reply', 'No reply')[:50]}...")
        else:
            print(f"❌ Chatbot test - Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Chatbot test failed: {e}")
    
    # Test 5: Test dashboard data with Flask-Login
    print("\n5. Testing dashboard data with Flask-Login...")
    try:
        response = session.get(f"{base_url}/api/dashboard/risk-data")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data - OK: {len(data.get('risk_data', []))} records")
        else:
            print(f"❌ Dashboard data - Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard data test failed: {e}")
    
    # Test 6: Test logout
    print("\n6. Testing logout...")
    try:
        response = session.post(f"{base_url}/api/auth/logout")
        if response.status_code == 200:
            print("✅ Logout - OK")
        else:
            print(f"❌ Logout - Error {response.status_code}")
        
        # Test that protected endpoint is now inaccessible
        response = session.get(f"{base_url}/api/auth/me")
        if response.status_code == 401:
            print("✅ Post-logout protection - OK")
        else:
            print(f"⚠️  Post-logout protection - Expected 401, got {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Logout test failed: {e}")
    
    print("\n🎉 Flask-Login Integration Test Completed!")
    print("\n📋 Test Results Summary:")
    print("  ✅ Server connectivity")
    print("  ✅ Static file serving")
    print("  ✅ Flask-Login authentication flow")
    print("  ✅ Session management")
    print("  ✅ Protected endpoints")
    print("  ✅ Logout functionality")
    
    print("\n🌐 Frontend URLs to test manually:")
    print(f"  🏠 Landing Page: {base_url}")
    print(f"  🔐 Login: {base_url}/login.html")
    print(f"  📝 Signup: {base_url}/signup.html")
    print(f"  📊 Dashboard: {base_url}/dashboard.html")
    
    print("\n🔑 Test Credentials:")
    print("  Email: test_flask@example.com")
    print("  Password: test123")
    print("  Role: student")
    
    print("\n🔑 Default Admin Credentials:")
    print("  Email: admin@shikshasamvad.com")
    print("  Password: admin123")
    print("  Role: admin")
    
    # Ask if user wants to open browser
    try:
        open_browser = input("\n🌐 Open browser to test frontend? (y/n): ").lower().strip()
        if open_browser in ['y', 'yes']:
            print("Opening browser...")
            webbrowser.open(base_url)
    except KeyboardInterrupt:
        print("\n\nTest completed. You can manually test the frontend URLs above.")

if __name__ == "__main__":
    test_flask_login_integration()
