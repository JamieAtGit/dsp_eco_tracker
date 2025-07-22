#!/usr/bin/env python3
"""
🔧 PyTest Configuration & Shared Fixtures
=========================================

Central configuration for the testing framework with shared fixtures,
mock data, and testing utilities used across all test modules.

Features:
- Mock Amazon product data
- Test configuration management
- Shared testing utilities
- Performance test markers
- Coverage configuration
"""

import pytest
import os
import sys
import json
from typing import Dict, Any, List
from unittest.mock import Mock, patch
import tempfile
import time

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Test markers
def pytest_configure(config):
    """Configure custom test markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for system interactions"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 5 seconds"
    )
    config.addinivalue_line(
        "markers", "network: Tests requiring network access"
    )

# Test Data Fixtures

@pytest.fixture
def sample_amazon_url():
    """Sample Amazon product URL for testing"""
    return "https://www.amazon.co.uk/Grenade-Protein-Powder-Serving-Servings/dp/B0CKFK6716"

@pytest.fixture
def invalid_urls():
    """Collection of invalid URLs for testing validation"""
    return [
        "",
        None,
        "not-a-url",
        "https://google.com",
        "amazon.co.uk/invalid",
        "https://amazon.co.uk/no-asin"
    ]

@pytest.fixture
def mock_product_data():
    """High-quality mock product data"""
    return {
        "title": "Grenade Whey Blend High Protein Powder, Low Sugar with 30g Protein per Serving, (12 Servings) - Fudged Up, 480 g (Pack of 1)",
        "origin": "England",
        "weight_kg": 0.48,
        "dimensions_cm": [20, 15, 10],
        "material_type": "Plastic",
        "recyclability": "Medium",
        "brand": "Grenade Store",
        "asin": "B0CKFK6716",
        "price": "£24.99",
        "data_quality_score": 95,
        "confidence": "High",
        "method": "Requests Scraping"
    }

@pytest.fixture
def low_quality_product_data():
    """Low-quality mock product data for testing fallbacks"""
    return {
        "title": "Unknown Product",
        "origin": "Unknown",
        "weight_kg": 1.0,
        "dimensions_cm": [15, 10, 8],
        "material_type": "Unknown",
        "recyclability": "Medium",
        "brand": "Unknown",
        "asin": "Unknown",
        "price": None,
        "data_quality_score": 25,
        "confidence": "Low",
        "method": "Fallback Analysis"
    }

@pytest.fixture
def mock_html_content():
    """Mock HTML content resembling Amazon product page"""
    return """
    <html>
    <head><title>Amazon Product</title></head>
    <body>
        <h1 id="productTitle">Grenade Whey Blend High Protein Powder</h1>
        <div id="bylineInfo">Grenade Store</div>
        <div class="product-details">
            <table>
                <tr><td>Weight</td><td>480 g</td></tr>
                <tr><td>Country of origin</td><td>Belgium</td></tr>
                <tr><td>Material</td><td>Plastic container</td></tr>
            </table>
        </div>
    </body>
    </html>
    """

@pytest.fixture
def mock_empty_html():
    """Mock empty/blocked HTML content"""
    return """
    <html>
    <body>
        <div>Access Denied</div>
        <div>Robot Check</div>
    </body>
    </html>
    """

# Mock Objects and Patches

@pytest.fixture
def mock_requests_response():
    """Mock successful HTTP response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'text/html'}
    mock_response.text = """
    <html>
        <h1 id="productTitle">Test Product</h1>
        <div id="bylineInfo">Test Brand</div>
    </html>
    """
    return mock_response

@pytest.fixture
def mock_requests_failure():
    """Mock failed HTTP response"""
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.headers = {'content-type': 'text/html'}
    mock_response.text = "Access Denied"
    return mock_response

@pytest.fixture
def mock_network_timeout():
    """Mock network timeout exception"""
    import requests
    return requests.exceptions.Timeout("Connection timeout")

# File System Fixtures

@pytest.fixture
def temp_directory():
    """Temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def temp_json_file(temp_directory):
    """Temporary JSON file for testing"""
    file_path = os.path.join(temp_directory, "test_data.json")
    test_data = {"test": "data", "items": [1, 2, 3]}
    
    with open(file_path, 'w') as f:
        json.dump(test_data, f)
    
    yield file_path

# Testing Utilities

@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed_ms(self):
            if self.start_time and self.end_time:
                return int((self.end_time - self.start_time) * 1000)
            return None
        
        def assert_faster_than(self, max_ms: int):
            """Assert operation completed within time limit"""
            assert self.elapsed_ms is not None, "Timer not started/stopped"
            assert self.elapsed_ms < max_ms, f"Operation took {self.elapsed_ms}ms, expected < {max_ms}ms"
    
    return Timer()

@pytest.fixture
def capture_logs(caplog):
    """Enhanced log capture with filtering"""
    class LogCapture:
        def __init__(self, caplog):
            self.caplog = caplog
        
        def assert_log_contains(self, message: str, level: str = "INFO"):
            """Assert log contains specific message at level"""
            found = any(
                message in record.message and record.levelname == level
                for record in self.caplog.records
            )
            assert found, f"Log message '{message}' at level {level} not found"
        
        def assert_no_errors(self):
            """Assert no ERROR or CRITICAL logs"""
            error_logs = [
                record for record in self.caplog.records
                if record.levelname in ["ERROR", "CRITICAL"]
            ]
            assert not error_logs, f"Unexpected error logs: {error_logs}"
        
        def get_logs_by_level(self, level: str) -> List[str]:
            """Get all log messages at specific level"""
            return [
                record.message for record in self.caplog.records
                if record.levelname == level
            ]
    
    return LogCapture(caplog)

# ML Model Fixtures

@pytest.fixture
def mock_xgboost_model():
    """Mock XGBoost model for testing"""
    mock_model = Mock()
    mock_model.predict.return_value = [2.5]  # Mock carbon emission prediction
    mock_model.feature_importances_ = [0.3, 0.2, 0.15, 0.1, 0.1, 0.05, 0.05, 0.05]
    return mock_model

@pytest.fixture
def sample_ml_features():
    """Sample feature vector for ML testing"""
    return [
        1,      # material_encoded
        0,      # transport_encoded  
        2,      # recyclability_encoded
        3,      # origin_encoded
        1.2,    # weight_log
        1,      # weight_bin_encoded
        0,      # packaging_type_encoded
        1,      # size_category_encoded
        2,      # quality_level_encoded
        1,      # inferred_category_encoded
        1,      # pack_size
        0.8,    # material_confidence
        0.9,    # origin_confidence
        0.7,    # weight_confidence
        5.0,    # estimated_lifespan_years
        0.6     # repairability_score
    ]

# Database/Cache Fixtures

@pytest.fixture
def mock_redis_cache():
    """Mock Redis cache for testing"""
    cache_data = {}
    
    class MockRedis:
        def get(self, key):
            return cache_data.get(key)
        
        def set(self, key, value, ex=None):
            cache_data[key] = value
            return True
        
        def delete(self, key):
            return cache_data.pop(key, None) is not None
        
        def flushall(self):
            cache_data.clear()
            return True
        
        def keys(self, pattern="*"):
            return list(cache_data.keys())
    
    return MockRedis()

# Environment Configuration

@pytest.fixture
def test_config():
    """Test configuration settings"""
    return {
        "TESTING": True,
        "CACHE_TTL": 60,  # Shorter TTL for testing
        "MAX_RETRIES": 2,
        "REQUEST_TIMEOUT": 5,
        "SCRAPING_DELAY": 0.1,  # Faster for tests
        "LOG_LEVEL": "DEBUG"
    }

@pytest.fixture(autouse=True)
def setup_test_environment(test_config):
    """Automatically setup test environment for all tests"""
    # Set environment variables
    original_env = {}
    for key, value in test_config.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = str(value)
    
    yield
    
    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

# Test Data Validation

def assert_product_data_structure(data: Dict[str, Any]):
    """Assert product data has required structure"""
    required_fields = [
        "title", "origin", "weight_kg", "dimensions_cm",
        "material_type", "recyclability", "brand", "asin"
    ]
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Type validation
    assert isinstance(data["title"], str), "Title must be string"
    assert isinstance(data["weight_kg"], (int, float)), "Weight must be numeric"
    assert isinstance(data["dimensions_cm"], list), "Dimensions must be list"
    assert len(data["dimensions_cm"]) == 3, "Dimensions must have 3 values"

def assert_quality_metrics(data: Dict[str, Any], min_quality: int = 0):
    """Assert quality metrics meet standards"""
    if "data_quality_score" in data:
        assert isinstance(data["data_quality_score"], int), "Quality score must be integer"
        assert 0 <= data["data_quality_score"] <= 100, "Quality score must be 0-100"
        assert data["data_quality_score"] >= min_quality, f"Quality below minimum {min_quality}"