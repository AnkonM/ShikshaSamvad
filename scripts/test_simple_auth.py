#!/usr/bin/env python3
"""
Test script for simple authentication system
"""
import requests
import json
import time

def test_simple_auth():
    """Test the simple authentication system"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Simple Authentication System...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
    except:
        print("❌ Cannot connect to server. Make sure it's running on port 5000")
        return
    
    # Test 2: Register a test user
    print("\n2. Testing user registration...")
    test_user = {
        "email": "test@example.com",
        "password": "test123",
        "first_name": "Test",
        "last_name": "User",
        "role": "student"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ User registration passed")
        else:
            print(f"❌ User registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test 3: Login
    print("\n3. Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login passed")
            session_cookie = response.cookies.get('session')
            print(f"   Session cookie: {session_cookie[:20]}...")
        else:
            print(f"❌ User login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 4: Get current user
    print("\n4. Testing get current user...")
    try:
        response = requests.get(f"{base_url}/api/auth/me", cookies=response.cookies)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Get user info passed: {user_data['user']['email']}")
        else:
            print(f"❌ Get user info failed: {response.text}")
    except Exception as e:
        print(f"❌ Get user error: {e}")
    
    # Test 5: Test chatbot endpoint
    print("\n5. Testing chatbot endpoint...")
    chat_data = {"text": "Hello, I'm feeling stressed"}
    
    try:
        response = requests.post(f"{base_url}/api/chatbot/chat", json=chat_data, cookies=response.cookies)
        if response.status_code == 200:
            chat_response = response.json()
            print(f"✅ Chatbot test passed: {chat_response['reply']}")
        else:
            print(f"❌ Chatbot test failed: {response.text}")
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
    
    # Test 6: Test dashboard data
    print("\n6. Testing dashboard data...")
    try:
        response = requests.get(f"{base_url}/api/dashboard/risk-data", cookies=response.cookies)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data test passed: {len(data.get('risk_data', []))} records")
        else:
            print(f"❌ Dashboard data test failed: {response.text}")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    # Test 7: Logout
    print("\n7. Testing logout...")
    try:
        response = requests.post(f"{base_url}/api/auth/logout", cookies=response.cookies)
        if response.status_code == 200:
            print("✅ Logout test passed")
        else:
            print(f"❌ Logout test failed: {response.text}")
    except Exception as e:
        print(f"❌ Logout error: {e}")
    
    print("\n🎉 Simple authentication system test completed!")
    print("\n📋 Next steps:")
    print("1. Open http://localhost:8501 in your browser")
    print("2. Login with test@example.com / test123")
    print("3. Explore the dashboard features")

if __name__ == "__main__":
    test_simple_auth()
