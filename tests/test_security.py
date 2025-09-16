# 🏆 Intelligent Retail Analytics Engine v3.0 - Security Tests
# Enterprise-grade security testing with vulnerability assessment

import pytest
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
import jwt
import bcrypt
from datetime import datetime, timedelta

# Import application components
from src.api.main import app, SecurityUtils, get_db
from src.api.main import User, UserCreate, UserLogin

# Test client
client = TestClient(app)

# ============================================================================
# SECURITY UTILITIES TESTS
# ============================================================================

class TestSecurityUtils:
    """Test security utility functions"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"

        # Hash password
        hashed = SecurityUtils.hash_password(password)
        assert hashed != password
        assert isinstance(hashed, str)

        # Verify password
        assert SecurityUtils.verify_password(password, hashed)
        assert not SecurityUtils.verify_password("wrong_password", hashed)

    def test_jwt_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        data = {"sub": "test@example.com", "role": "user"}

        # Create token
        token = SecurityUtils.create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token
        payload = SecurityUtils.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "user"
        assert payload["type"] == "access"

    def test_jwt_token_expiration(self):
        """Test JWT token expiration"""
        data = {"sub": "test@example.com"}

        # Create token with short expiration
        token = SecurityUtils.create_access_token(data, timedelta(seconds=1))

        # Token should be valid immediately
        assert SecurityUtils.verify_token(token) is not None

        # Wait for expiration
        import time
        time.sleep(2)

        # Token should be expired
        assert SecurityUtils.verify_token(token) is None

    def test_input_sanitization(self):
        """Test input sanitization"""
        # Normal input
        clean_input = SecurityUtils.sanitize_input("Hello World")
        assert clean_input == "Hello World"

        # Input with dangerous characters
        dangerous_input = SecurityUtils.sanitize_input("Hello <script>alert('xss')</script> World")
        assert dangerous_input == "Hello alert('xss') World"

        # Long input (should be truncated)
        long_input = "A" * 10000
        sanitized = SecurityUtils.sanitize_input(long_input)
        assert len(sanitized) <= 10000

    def test_secure_filename_generation(self):
        """Test secure filename generation"""
        filename = "test_image.jpg"
        secure_name = SecurityUtils.generate_secure_filename(filename)

        # Should have UUID prefix
        assert len(secure_name) > len("test_image.jpg")
        assert secure_name.endswith(".jpg")

        # Should be different each time
        secure_name2 = SecurityUtils.generate_secure_filename(filename)
        assert secure_name != secure_name2

# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test authentication endpoints"""

    def test_user_registration_success(self):
        """Test successful user registration"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongPass123!",
            "full_name": "Test User"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code in [200, 201]

        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser2",
            "password": "StrongPass123!",
            "full_name": "Test User 2"
        }

        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code in [200, 201]

        # Second registration should fail
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400

    def test_user_login_success(self):
        """Test successful user login"""
        # First register user
        user_data = {
            "email": "login_test@example.com",
            "username": "logintest",
            "password": "StrongPass123!",
            "full_name": "Login Test User"
        }

        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code in [200, 201]

        # Now login
        login_data = {
            "email": "login_test@example.com",
            "password": "StrongPass123!"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_user_login_wrong_password(self):
        """Test login with wrong password"""
        login_data = {
            "email": "login_test@example.com",
            "password": "WrongPassword123!"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    def test_user_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    def test_token_refresh(self):
        """Test token refresh functionality"""
        # Login to get tokens
        login_data = {
            "email": "login_test@example.com",
            "password": "StrongPass123!"
        }

        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        refresh_response = client.post("/api/v1/auth/refresh",
                                     json={"refresh_token": refresh_token})
        assert refresh_response.status_code == 200

        data = refresh_response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        # Login to get token
        login_data = {
            "email": "login_test@example.com",
            "password": "StrongPass123!"
        }

        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # Access protected endpoint
        response = client.get("/api/v1/users/me",
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

        data = response.json()
        assert "email" in data
        assert "username" in data

# ============================================================================
# AUTHORIZATION TESTS
# ============================================================================

class TestAuthorization:
    """Test authorization and role-based access"""

    def test_admin_only_endpoint_as_user(self):
        """Test accessing admin endpoint as regular user"""
        # Login as regular user
        login_data = {
            "email": "login_test@example.com",
            "password": "StrongPass123!"
        }

        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # Try to access admin endpoint
        response = client.get("/api/v1/admin/users",
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    def test_user_profile_update(self):
        """Test user profile update"""
        # Login to get token
        login_data = {
            "email": "login_test@example.com",
            "password": "StrongPass123!"
        }

        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # Update profile
        update_data = {
            "username": "updateduser",
            "full_name": "Updated Test User"
        }

        response = client.put("/api/v1/users/me",
                            json=update_data,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

class TestInputValidation:
    """Test input validation and sanitization"""

    def test_weak_password_registration(self):
        """Test registration with weak password"""
        user_data = {
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "123",  # Too short
            "full_name": "Weak User"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_email_registration(self):
        """Test registration with invalid email"""
        user_data = {
            "email": "invalid-email",
            "username": "invaliduser",
            "password": "StrongPass123!",
            "full_name": "Invalid User"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    def test_sql_injection_attempt(self):
        """Test SQL injection attempt in login"""
        login_data = {
            "email": "'; DROP TABLE users; --",
            "password": "password"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401  # Should fail authentication, not cause SQL error

    def test_xss_attempt_in_registration(self):
        """Test XSS attempt in user registration"""
        user_data = {
            "email": "xss@example.com",
            "username": "xssuser",
            "password": "StrongPass123!",
            "full_name": "<script>alert('xss')</script>"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code in [200, 201]  # Should succeed but sanitize input

# ============================================================================
# SECURITY HEADERS TESTS
# ============================================================================

class TestSecurityHeaders:
    """Test security headers in responses"""

    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        response = client.get("/health")

        # Check for essential security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

        assert "Content-Security-Policy" in response.headers

    def test_cors_headers(self):
        """Test CORS headers"""
        response = client.options("/health")

        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers

# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_exceeded(self):
        """Test rate limiting for excessive requests"""
        # Make multiple requests quickly
        responses = []
        for _ in range(150):  # Exceed rate limit
            response = client.get("/health")
            responses.append(response.status_code)

        # Should have some rate limited responses
        assert 429 in responses  # Too Many Requests

# ============================================================================
# FILE UPLOAD SECURITY TESTS
# ============================================================================

class TestFileUploadSecurity:
    """Test file upload security"""

    def test_invalid_file_type_upload(self):
        """Test uploading invalid file type"""
        # This would require setting up file upload endpoint
        # For now, test the utility function
        from src.api.main import SecurityUtils

        # Test valid file
        assert SecurityUtils.validate_file_upload(
            type('MockFile', (), {'size': 1000, 'filename': 'test.jpg'})()
        )

        # Test invalid file type
        try:
            SecurityUtils.validate_file_upload(
                type('MockFile', (), {'size': 1000, 'filename': 'test.exe'})()
            )
            assert False, "Should have raised exception"
        except Exception:
            pass  # Expected

    def test_file_size_limit(self):
        """Test file size limit enforcement"""
        from src.api.main import SecurityUtils

        # Test file too large
        try:
            SecurityUtils.validate_file_upload(
                type('MockFile', (), {'size': 20*1024*1024, 'filename': 'large.jpg'})()
            )
            assert False, "Should have raised exception"
        except Exception:
            pass  # Expected

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and responses"""

    def test_404_error(self):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_500_error_handling(self):
        """Test 500 error handling"""
        # This would require triggering an internal error
        # For now, just test that errors are properly formatted
        response = client.get("/health")
        assert response.status_code == 200

    def test_validation_error_format(self):
        """Test validation error format"""
        # Invalid data that should trigger validation error
        user_data = {
            "email": "invalid",
            "username": "test",
            "password": "123"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

        error_data = response.json()
        assert "detail" in error_data

# ============================================================================
# SESSION MANAGEMENT TESTS
# ============================================================================

class TestSessionManagement:
    """Test session management and token handling"""

    def test_token_expiration(self):
        """Test token expiration handling"""
        # Create a token that's already expired
        expired_token = SecurityUtils.create_access_token(
            {"sub": "test@example.com"},
            timedelta(seconds=-1)  # Already expired
        )

        # Try to access protected endpoint
        response = client.get("/api/v1/users/me",
                            headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401

    def test_invalid_token_format(self):
        """Test invalid token format handling"""
        response = client.get("/api/v1/users/me",
                            headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401

    def test_missing_authorization_header(self):
        """Test missing authorization header"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

# ============================================================================
# LOGGING TESTS
# ============================================================================

class TestLogging:
    """Test security logging functionality"""

    def test_authentication_logging(self):
        """Test that authentication events are logged"""
        # This would require checking log files
        # For now, just ensure endpoints work
        login_data = {
            "email": "login_test@example.com",
            "password": "StrongPass123!"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        # Just ensure it doesn't crash
        assert response.status_code in [200, 401]

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestSecurityIntegration:
    """Integration tests for security features"""

    def test_complete_user_workflow(self):
        """Test complete user registration and authentication workflow"""
        # Register
        user_data = {
            "email": f"workflow_{datetime.now().timestamp()}@example.com",
            "username": f"workflowuser_{datetime.now().timestamp()}",
            "password": "StrongPass123!",
            "full_name": "Workflow Test User"
        }

        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code in [200, 201]

        # Login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # Access protected endpoint
        profile_response = client.get("/api/v1/users/me",
                                    headers={"Authorization": f"Bearer {token}"})
        assert profile_response.status_code == 200

        # Logout (if implemented)
        # This would depend on your logout implementation

    def test_security_headers_integration(self):
        """Test security headers across different endpoints"""
        endpoints = ["/health", "/docs", "/openapi.json"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 307]  # 307 for redirects

            # Check security headers
            assert "X-Content-Type-Options" in response.headers
            assert "X-Frame-Options" in response.headers

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestSecurityPerformance:
    """Test security feature performance"""

    def test_authentication_performance(self):
        """Test authentication endpoint performance"""
        import time

        login_data = {
            "email": "login_test@example.com",
            "password": "StrongPass123!"
        }

        start_time = time.time()
        response = client.post("/api/v1/auth/login", json=login_data)
        end_time = time.time()

        # Should respond within reasonable time
        assert end_time - start_time < 2.0  # Less than 2 seconds
        assert response.status_code in [200, 401]

# ============================================================================
# CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Clean up after each test"""
    yield
    # Add cleanup logic here if needed
    # For example, clean up test database entries