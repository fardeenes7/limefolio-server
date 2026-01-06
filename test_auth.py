#!/usr/bin/env python
"""
Quick test script to verify authentication endpoints
Run this after starting the server with: python manage.py runserver
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/auth"

def test_registration():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    url = f"{BASE_URL}/registration/"
    data = {
        "email": "test@example.com",
        "password1": "TestPassword123!",
        "password2": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login(email, password):
    """Test user login"""
    print("\n=== Testing Login ===")
    url = f"{BASE_URL}/login/"
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_user_profile(access_token):
    """Test getting user profile"""
    print("\n=== Testing User Profile ===")
    url = f"{BASE_URL}/user/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_token_refresh(refresh_token):
    """Test token refresh"""
    print("\n=== Testing Token Refresh ===")
    url = f"{BASE_URL}/token/refresh/"
    data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_logout(refresh_token):
    """Test logout"""
    print("\n=== Testing Logout ===")
    url = f"{BASE_URL}/logout/"
    data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("Authentication API Test Suite")
    print("=" * 50)
    print("\nMake sure the server is running: python manage.py runserver")
    print("Press Enter to continue...")
    input()
    
    # Test registration
    reg_result = test_registration()
    
    if reg_result and 'access' in reg_result:
        access_token = reg_result['access']
        refresh_token = reg_result['refresh']
        
        # Test user profile
        test_user_profile(access_token)
        
        # Test token refresh
        refresh_result = test_token_refresh(refresh_token)
        
        if refresh_result and 'access' in refresh_result:
            new_access_token = refresh_result['access']
            new_refresh_token = refresh_result.get('refresh', refresh_token)
            
            # Test logout
            test_logout(new_refresh_token)
    else:
        # If registration fails (user might exist), try login
        print("\nRegistration failed, trying login...")
        login_result = test_login("test@example.com", "TestPassword123!")
        
        if login_result and 'access' in login_result:
            access_token = login_result['access']
            refresh_token = login_result['refresh']
            
            # Test user profile
            test_user_profile(access_token)
            
            # Test token refresh
            refresh_result = test_token_refresh(refresh_token)
            
            if refresh_result and 'access' in refresh_result:
                new_refresh_token = refresh_result.get('refresh', refresh_token)
                
                # Test logout
                test_logout(new_refresh_token)
    
    print("\n" + "=" * 50)
    print("Test Suite Complete!")
    print("=" * 50)
