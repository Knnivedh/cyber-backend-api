#!/usr/bin/env python3
"""
API Test Script
"""

import requests
import time

def test_api():
    print("🧪 Testing Cyber Intelligence API")
    print("=" * 50)

    try:
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            print("✅ Root endpoint: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")

        # Test stats endpoint
        print("\nTesting stats endpoint...")
        response = requests.get('http://localhost:8000/stats')
        if response.status_code == 200:
            print("✅ Stats endpoint: OK")
            data = response.json()
            print(f"   Total records: {data['database_stats']['expert_knowledge']}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")

        # Test search endpoint
        print("\nTesting search endpoint...")
        response = requests.get('http://localhost:8000/search?query=ciso&limit=2')
        if response.status_code == 200:
            print("✅ Search endpoint: OK")
            data = response.json()
            print(f"   Found {data['total_results']} results")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")

        print("\n🎉 All tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api()
