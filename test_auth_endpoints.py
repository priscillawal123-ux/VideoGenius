#!/usr/bin/env python3
"""
Test script for Video Genius authentication endpoints.
"""

import sys
import os
import time
import subprocess
import requests
import json
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_server() -> subprocess.Popen:
    """Start the FastAPI server."""
    print("Starting Video Genius server...")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))

    process = subprocess.Popen(
        [
            "python",
            "-m",
            "uvicorn",
            "backend.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--log-level",
            "warning",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(3)
    return process


def test_health_check() -> bool:
    """Test the health check endpoint."""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_user_registration() -> Optional[dict]:
    """Test user registration."""
    try:
        data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpass123",
        }
        response = requests.post(
            "http://127.0.0.1:8000/auth/register", json=data, timeout=5
        )

        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ User registration successful: {user_data['email']}")
            return user_data
        else:
            print(
                f"✗ User registration failed: {response.status_code} - {response.text}"
            )
            return None
    except Exception as e:
        print(f"✗ User registration error: {e}")
        return None


def test_user_login() -> Optional[str]:
    """Test user login and return access token."""
    try:
        data = {"username": "test@example.com", "password": "testpass123"}
        response = requests.post(
            "http://127.0.0.1:8000/auth/login", data=data, timeout=5
        )

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✓ User login successful, token received")
            return access_token
        else:
            print(f"✗ User login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ User login error: {e}")
        return None


def test_get_current_user(access_token: str) -> bool:
    """Test getting current user info with token."""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "http://127.0.0.1:8000/auth/me", headers=headers, timeout=5
        )

        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ Get current user successful: {user_data['email']}")
            return True
        else:
            print(
                f"✗ Get current user failed: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        print(f"✗ Get current user error: {e}")
        return False


def test_token_refresh(access_token: str) -> bool:
    """Test token refresh."""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(
            "http://127.0.0.1:8000/auth/refresh", headers=headers, timeout=5
        )

        if response.status_code == 200:
            new_token_data = response.json()
            print("✓ Token refresh successful")
            return True
        else:
            print(f"✗ Token refresh failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Token refresh error: {e}")
        return False


def test_protected_route_without_token() -> bool:
    """Test accessing protected route without token."""
    try:
        response = requests.get("http://127.0.0.1:8000/auth/me", timeout=5)

        if response.status_code == 401:
            print("✓ Protected route correctly rejects unauthorized access")
            return True
        else:
            print(
                f"✗ Protected route should reject unauthorized access: {response.status_code}"
            )
            return False
    except Exception as e:
        print(f"✗ Protected route test error: {e}")
        return False


def main():
    """Run all authentication tests."""
    print("=== Video Genius Authentication Tests ===\n")

    # Start server
    server_process = start_server()

    try:
        # Test 1: Health check
        print("1. Testing health check...")
        health_ok = test_health_check()

        if not health_ok:
            print("Server is not responding. Exiting tests.")
            return

        # Test 2: User registration
        print("\n2. Testing user registration...")
        user_data = test_user_registration()

        if not user_data:
            print("User registration failed. Exiting tests.")
            return

        # Test 3: User login
        print("\n3. Testing user login...")
        access_token = test_user_login()

        if not access_token:
            print("User login failed. Exiting tests.")
            return

        # Test 4: Get current user
        print("\n4. Testing get current user...")
        current_user_ok = test_get_current_user(access_token)

        # Test 5: Token refresh
        print("\n5. Testing token refresh...")
        refresh_ok = test_token_refresh(access_token)

        # Test 6: Protected route without token
        print("\n6. Testing protected route without token...")
        protected_no_token_ok = test_protected_route_without_token()

        # Summary
        print("\n=== Test Results ===")
        tests = [
            ("Health Check", health_ok),
            ("User Registration", user_data is not None),
            ("User Login", access_token is not None),
            ("Get Current User", current_user_ok),
            ("Token Refresh", refresh_ok),
            ("Protected Route (No Token)", protected_no_token_ok),
        ]

        passed = 0
        for test_name, result in tests:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1

        print(f"\nPassed: {passed}/{len(tests)} tests")

        if passed == len(tests):
            print("🎉 All authentication tests passed!")
        else:
            print("❌ Some tests failed. Check the output above.")

    finally:
        # Clean up
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    main()
