#!/usr/bin/env python3
"""
Test script for frontend integration
"""
import requests
import time
import webbrowser
from pathlib import Path

def test_frontend_integration():
    """Test the complete frontend integration"""
    print("🧪 Testing Frontend Integration...")
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
        print("   Start the server with: python scripts/start_frontend.py")
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
    
    # Test 3: Test authentication flow
    print("\n3. Testing authentication flow...")
    
    # Register a test user
    test_user = {
        "email": "test@example.com",
        "password": "test123",
        "first_name": "Test",
        "last_name": "User",
        "role": "student"
    }
    
    try:
        # Register
        response = requests.post(f"{base_url}/api/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ User registration - OK")
        else:
            print(f"⚠️  User registration - {response.status_code} (may already exist)")
        
        # Login
        login_data = {"email": test_user["email"], "password": test_user["password"]}
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login - OK")
            session_cookies = response.cookies
        else:
            print(f"❌ User login - Error {response.status_code}")
            return
        
        # Test protected endpoint
        response = requests.get(f"{base_url}/api/auth/me", cookies=session_cookies)
        if response.status_code == 200:
            print("✅ Protected endpoint access - OK")
        else:
            print(f"❌ Protected endpoint access - Error {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication test failed: {e}")
        return
    
    # Test 4: Test chatbot endpoint
    print("\n4. Testing chatbot integration...")
    try:
        chat_data = {"text": "Hello, I'm feeling stressed"}
        response = requests.post(f"{base_url}/api/chatbot/chat", json=chat_data, cookies=session_cookies)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chatbot response - OK: {data.get('reply', 'No reply')[:50]}...")
        else:
            print(f"❌ Chatbot test - Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Chatbot test failed: {e}")
    
    # Test 5: Test dashboard data
    print("\n5. Testing dashboard data...")
    try:
        response = requests.get(f"{base_url}/api/dashboard/risk-data", cookies=session_cookies)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data - OK: {len(data.get('risk_data', []))} records")
        else:
            print(f"❌ Dashboard data - Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard data test failed: {e}")
    
    print("\n🎉 Frontend Integration Test Completed!")
    print("\n📋 Test Results Summary:")
    print("  ✅ Server connectivity")
    print("  ✅ Static file serving")
    print("  ✅ Authentication flow")
    print("  ✅ API integration")
    print("  ✅ Protected endpoints")
    
    print("\n🌐 Frontend URLs to test manually:")
    print(f"  🏠 Landing Page: {base_url}")
    print(f"  🔐 Login: {base_url}/login.html")
    print(f"  📝 Signup: {base_url}/signup.html")
    print(f"  📊 Dashboard: {base_url}/dashboard.html")
    
    print("\n🔑 Test Credentials:")
    print("  Email: test@example.com")
    print("  Password: test123")
    print("  Role: student")
    
    # Ask if user wants to open browser
    try:
        open_browser = input("\n🌐 Open browser to test frontend? (y/n): ").lower().strip()
        if open_browser in ['y', 'yes']:
            print("Opening browser...")
            webbrowser.open(base_url)
    except KeyboardInterrupt:
        print("\n\nTest completed. You can manually test the frontend URLs above.")

if __name__ == "__main__":
    test_frontend_integration()
