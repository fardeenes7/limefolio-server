"""
Quick test script to verify Experience and Skills API endpoints.
Run this after authenticating to test the Dashboard API.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
# Replace with your actual access token
ACCESS_TOKEN = "your_access_token_here"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def test_dashboard_api():
    """Test Dashboard API endpoints"""
    print("=" * 60)
    print("Testing Dashboard API")
    print("=" * 60)
    
    # Test Experiences List
    print("\n1. Testing GET /api/dashboard/experiences/")
    response = requests.get(f"{BASE_URL}/api/dashboard/experiences/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Experiences: {len(response.json())} found")
    else:
        print(f"Error: {response.text}")
    
    # Test Skills List
    print("\n2. Testing GET /api/dashboard/skills/")
    response = requests.get(f"{BASE_URL}/api/dashboard/skills/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Skills: {len(response.json())} found")
    else:
        print(f"Error: {response.text}")
    
    # Test Social Links List
    print("\n3. Testing GET /api/dashboard/social-links/")
    response = requests.get(f"{BASE_URL}/api/dashboard/social-links/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Social Links: {len(response.json())} found")
    else:
        print(f"Error: {response.text}")
    
    # Test Create Skill
    print("\n4. Testing POST /api/dashboard/skills/")
    skill_data = {
        "name": "Django",
        "category": "framework",
        "proficiency": "expert",
        "description": "Expert in Django web framework",
        "years_of_experience": 5,
        "is_featured": True,
        "is_published": True,
        "order": 0
    }
    response = requests.post(
        f"{BASE_URL}/api/dashboard/skills/", 
        headers=headers,
        json=skill_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        skill = response.json()
        print(f"Created Skill: {skill['name']} ({skill['proficiency_display']})")
        return skill['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_public_api(subdomain="test"):
    """Test Public API endpoints"""
    print("\n" + "=" * 60)
    print("Testing Public API")
    print("=" * 60)
    print(f"Note: Requires site detection via domain: {subdomain}.limefolio.com")
    
    # These would work with proper domain setup
    print("\n1. GET /api/public/experiences/")
    print("2. GET /api/public/skills/")
    print("3. GET /api/public/social-links/")
    print("\nSkipping public API tests (requires domain setup)")

def test_external_api(api_key="", api_secret=""):
    """Test External API endpoints"""
    print("\n" + "=" * 60)
    print("Testing External API")
    print("=" * 60)
    
    if not api_key or not api_secret:
        print("Skipping external API tests (requires API key and secret)")
        return
    
    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret
    }
    
    print("\n1. Testing GET /v1/experiences/")
    response = requests.get(f"{BASE_URL}/v1/experiences/", headers=headers)
    print(f"Status: {response.status_code}")
    
    print("\n2. Testing GET /v1/skills/")
    response = requests.get(f"{BASE_URL}/v1/skills/", headers=headers)
    print(f"Status: {response.status_code}")

if __name__ == "__main__":
    print("\n🚀 Experience & Skills API Test Suite\n")
    
    if ACCESS_TOKEN == "your_access_token_here":
        print("⚠️  Please set your ACCESS_TOKEN in the script first!")
        print("You can get it by logging in via the OAuth flow.")
    else:
        test_dashboard_api()
        test_public_api()
        test_external_api()
    
    print("\n✅ Test suite completed!\n")
