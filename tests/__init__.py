# 🏆 Intelligent Retail Analytics Engine v3.0 - Test Suite
# Enterprise-grade testing framework with security and performance validation

"""
Test suite for Intelligent Retail Analytics Engine v3.0

This module provides comprehensive testing capabilities including:
- Unit tests for all components
- Integration tests for system interactions
- Performance tests for scalability validation
- Security tests for vulnerability assessment
- End-to-end tests for complete workflows

Test Categories:
- Unit Tests: Individual component testing
- Integration Tests: Component interaction testing
- Performance Tests: Scalability and speed validation
- Security Tests: Vulnerability and penetration testing
- E2E Tests: Complete user journey testing
"""

import os
import sys
import pytest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test configuration
TEST_CONFIG = {
    "test_data_dir": Path(__file__).parent / "test_data",
    "fixtures_dir": Path(__file__).parent / "fixtures",
    "performance_thresholds": {
        "api_response_time": 2.0,  # seconds
        "database_query_time": 1.0,  # seconds
        "bigquery_query_time": 30.0,  # seconds
        "memory_usage": 500 * 1024 * 1024,  # 500MB
        "cpu_usage": 80.0,  # percentage
    },
    "security_checks": {
        "max_vulnerabilities": 0,
        "max_warnings": 5,
        "required_headers": [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Content-Security-Policy"
        ]
    }
}

# Create test directories if they don't exist
TEST_CONFIG["test_data_dir"].mkdir(exist_ok=True)
TEST_CONFIG["fixtures_dir"].mkdir(exist_ok=True)

# Test fixtures and utilities
def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "bigquery: Tests requiring BigQuery")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file paths"""
    for item in items:
        # Add markers based on file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Mark slow tests
        if "performance" in str(item.fspath) or "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

# Global test fixtures
@pytest.fixture(scope="session")
def test_config():
    """Global test configuration"""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory fixture"""
    return TEST_CONFIG["test_data_dir"]

@pytest.fixture(scope="session")
def fixtures_dir():
    """Test fixtures directory fixture"""
    return TEST_CONFIG["fixtures_dir"]

# Environment setup for tests
def setup_test_environment():
    """Setup test environment variables"""
    os.environ.setdefault("APP_ENV", "test")
    os.environ.setdefault("DEBUG", "True")
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
    os.environ.setdefault("LOG_LEVEL", "WARNING")

# Call setup on import
setup_test_environment()

# Export test utilities
__all__ = [
    "TEST_CONFIG",
    "test_config",
    "test_data_dir",
    "fixtures_dir",
    "setup_test_environment"
]