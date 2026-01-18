"""
Test script to verify the API works correctly.
Run this locally before deploying to Railway.
"""
import requests
import json

# Test the API
BASE_URL = "http://localhost:8000"  # Change to your Railway URL after deployment

def test_health():
    """Test health endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_root():
    """Test root endpoint."""
    response = requests.get(f"{BASE_URL}/")
    print(f"Root Endpoint: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_prayer_times():
    """Test prayer times calculation."""
    payload = {
        "latitude": 59.9139,  # Oslo
        "longitude": 10.7522,
        "date": "2025-01-15",
        "country": "norway"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/times/daily", json=payload)
    print(f"Prayer Times: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Fajr: {data['prayer_times']['fajr']}")
        print(f"Qibla: {data['qibla_direction']}°")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_qibla():
    """Test Qibla calculation."""
    payload = {
        "latitude": 59.9139,
        "longitude": 10.7522
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/qibla", json=payload)
    print(f"Qibla: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Qibla Direction: {data['qibla_direction']}°")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("Testing Salah Prayer API...\n")
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Prayer Times", test_prayer_times),
        ("Qibla", test_qibla)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✓ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Ready for deployment!")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
