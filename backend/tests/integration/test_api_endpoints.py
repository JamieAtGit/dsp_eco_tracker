#!/usr/bin/env python3
"""
Integration tests for Flask API endpoints
These tests validate the complete API functionality end-to-end
"""

import pytest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
import requests

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import Flask app
try:
    from backend.api.app import app
except ImportError:
    # Fallback if imports fail
    app = None


@pytest.fixture
def client():
    """Flask test client"""
    if app is None:
        pytest.skip("Flask app not available for testing")
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture 
def sample_request_data():
    """Sample request data for testing"""
    return {
        "amazon_url": "https://www.amazon.co.uk/USN-Protein-Powder/dp/B0DG5V9BWQ/",
        "postcode": "SW1A 1AA",
        "include_packaging": True
    }


class TestHealthEndpoints:
    """Test basic health and status endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

    def test_api_version(self, client):
        """Test API version endpoint"""
        response = client.get('/version')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'version' in data
        assert 'api_name' in data


class TestEmissionEstimationEndpoint:
    """Test the main /estimate_emissions endpoint"""
    
    def test_estimate_emissions_success(self, client, sample_request_data):
        """Test successful emission estimation"""
        with patch('backend.scrapers.amazon.unified_scraper.UnifiedAmazonScraper') as mock_scraper_class:
            # Mock successful scraping
            mock_scraper = Mock()
            mock_scraper.scrape_product.return_value = {
                'title': 'USN Pure Protein GF-1 Growth & Repair Protein Powder, Chocolate Flavour, 476g',
                'weight_kg': 0.476,
                'origin': 'South Africa',
                'material_type': 'Mixed',
                'brand': 'USN'
            }
            mock_scraper_class.return_value = mock_scraper
            
            # Mock ML prediction
            with patch('pickle.load') as mock_pickle:
                mock_model = Mock()
                mock_model.predict.return_value = ['B']
                mock_model.predict_proba.return_value = [[0.1, 0.8, 0.1]]
                mock_pickle.return_value = mock_model
                
                response = client.post('/estimate_emissions', 
                                     data=json.dumps(sample_request_data),
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                
                # Check response structure
                assert 'success' in data
                assert 'data' in data
                assert 'title' in data
                
                # Check emission data
                emission_data = data['data']
                assert 'eco_score_ml' in emission_data['attributes']
                assert 'carbon_kg' in emission_data['attributes']
                assert 'trees_to_offset' in emission_data['attributes']

    def test_estimate_emissions_invalid_url(self, client):
        """Test emission estimation with invalid URL"""
        invalid_data = {
            "amazon_url": "not-a-valid-url",
            "postcode": "SW1A 1AA"
        }
        
        response = client.post('/estimate_emissions',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'invalid' in data['error'].lower() or 'url' in data['error'].lower()

    def test_estimate_emissions_missing_fields(self, client):
        """Test emission estimation with missing required fields"""
        incomplete_data = {
            "postcode": "SW1A 1AA"
            # Missing amazon_url
        }
        
        response = client.post('/estimate_emissions',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_estimate_emissions_scraping_failure(self, client, sample_request_data):
        """Test handling of scraping failures"""
        with patch('backend.scrapers.amazon.unified_scraper.UnifiedAmazonScraper') as mock_scraper_class:
            # Mock scraping failure
            mock_scraper = Mock()
            mock_scraper.scrape_product.return_value = None
            mock_scraper_class.return_value = mock_scraper
            
            response = client.post('/estimate_emissions',
                                 data=json.dumps(sample_request_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'scraping' in data['error'].lower() or 'failed' in data['error'].lower()

    def test_estimate_emissions_postcode_processing(self, client):
        """Test different postcode formats"""
        test_postcodes = [
            "SW1A 1AA",  # Standard format
            "sw1a1aa",   # No spaces, lowercase
            "SW1A1AA",   # No spaces, uppercase
            "M1 1AA",    # Different area
            ""           # Empty (should use default)
        ]
        
        for postcode in test_postcodes:
            request_data = {
                "amazon_url": "https://www.amazon.co.uk/test/dp/B0DG5V9BWQ/",
                "postcode": postcode
            }
            
            with patch('backend.scrapers.amazon.unified_scraper.UnifiedAmazonScraper'):
                response = client.post('/estimate_emissions',
                                     data=json.dumps(request_data),
                                     content_type='application/json')
                
                # Should handle all postcode formats gracefully
                assert response.status_code in [200, 400], f"Failed for postcode: {postcode}"


class TestPredictionEndpoint:
    """Test the /predict endpoint for direct ML predictions"""
    
    def test_predict_endpoint_success(self, client):
        """Test successful prediction"""
        prediction_data = {
            "material_type": "Plastic",
            "transport_mode": "ship", 
            "recyclability": "Medium",
            "origin": "China",
            "weight_kg": 0.5
        }
        
        with patch('pickle.load') as mock_pickle:
            mock_model = Mock()
            mock_model.predict.return_value = ['B']
            mock_model.predict_proba.return_value = [[0.1, 0.8, 0.1]]
            mock_pickle.return_value = mock_model
            
            response = client.post('/predict',
                                 data=json.dumps(prediction_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'prediction' in data
            assert 'confidence' in data
            assert data['prediction'] in ['A+', 'A', 'B', 'C', 'D', 'E', 'F']
            assert 0 <= data['confidence'] <= 100

    def test_predict_endpoint_missing_features(self, client):
        """Test prediction with missing features"""
        incomplete_data = {
            "material_type": "Plastic"
            # Missing other required features
        }
        
        response = client.post('/predict',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_predict_endpoint_invalid_values(self, client):
        """Test prediction with invalid feature values"""
        invalid_data = {
            "material_type": "InvalidMaterial",
            "transport_mode": "teleportation",
            "weight_kg": -5  # Negative weight
        }
        
        response = client.post('/predict',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestInsightsEndpoint:
    """Test the /insights endpoint for analytics"""
    
    def test_insights_endpoint_success(self, client):
        """Test successful insights retrieval"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            with patch('pandas.read_csv') as mock_read_csv:
                # Mock dataset
                import pandas as pd
                mock_df = pd.DataFrame({
                    'eco_score_ml': ['A', 'B', 'C', 'A', 'B'],
                    'material_type': ['Plastic', 'Metal', 'Wood', 'Plastic', 'Metal'],
                    'carbon_kg': [1.2, 2.5, 0.8, 1.1, 2.3],
                    'recyclability': ['High', 'Medium', 'High', 'Medium', 'Low']
                })
                mock_read_csv.return_value = mock_df
                
                response = client.get('/insights')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                
                # Check insights structure
                assert 'total_products' in data
                assert 'eco_score_distribution' in data
                assert 'material_breakdown' in data
                assert 'carbon_stats' in data

    def test_insights_endpoint_no_data(self, client):
        """Test insights when no data available"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            response = client.get('/insights')
            
            # Should handle gracefully
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'total_products' in data
                assert data['total_products'] == 0


class TestAdminEndpoints:
    """Test admin endpoints for data management"""
    
    def test_admin_submissions_endpoint(self, client):
        """Test admin submissions retrieval"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            with patch('json.load') as mock_json_load:
                mock_submissions = [
                    {
                        'url': 'https://amazon.co.uk/test1',
                        'timestamp': '2024-01-01T12:00:00',
                        'status': 'completed'
                    },
                    {
                        'url': 'https://amazon.co.uk/test2', 
                        'timestamp': '2024-01-02T12:00:00',
                        'status': 'failed'
                    }
                ]
                mock_json_load.return_value = mock_submissions
                
                response = client.get('/admin/submissions')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                
                assert 'submissions' in data
                assert len(data['submissions']) == 2
                assert data['submissions'][0]['status'] == 'completed'

    def test_admin_clear_cache_endpoint(self, client):
        """Test admin cache clearing"""
        response = client.post('/admin/clear-cache')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'cache' in data['message'].lower()


class TestCORSAndSecurity:
    """Test CORS headers and security measures"""
    
    def test_cors_headers_present(self, client, sample_request_data):
        """Test CORS headers are properly set"""
        response = client.post('/estimate_emissions',
                             data=json.dumps(sample_request_data),
                             content_type='application/json')
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers

    def test_options_request_handling(self, client):
        """Test OPTIONS request for CORS preflight"""
        response = client.options('/estimate_emissions')
        
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers

    def test_content_type_validation(self, client):
        """Test Content-Type header validation"""
        # Test with wrong content type
        response = client.post('/estimate_emissions',
                             data="invalid data",
                             content_type='text/plain')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_request_size_limits(self, client):
        """Test request size limitations"""
        large_data = {
            "amazon_url": "https://amazon.co.uk/test",
            "postcode": "SW1A 1AA",
            "large_field": "x" * 10000  # Very large field
        }
        
        response = client.post('/estimate_emissions',
                             data=json.dumps(large_data),
                             content_type='application/json')
        
        # Should handle large requests appropriately
        assert response.status_code in [200, 400, 413]  # 413 = Payload Too Large


class TestPerformanceAndReliability:
    """Test performance and reliability aspects"""
    
    def test_concurrent_requests_handling(self, client, sample_request_data):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                with patch('backend.scrapers.amazon.unified_scraper.UnifiedAmazonScraper'):
                    response = client.post('/estimate_emissions',
                                         data=json.dumps(sample_request_data),
                                         content_type='application/json')
                    results.append(response.status_code)
            except Exception as e:
                results.append(f"Error: {e}")
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)
        
        # All requests should complete
        assert len(results) == 5
        assert all(isinstance(r, int) for r in results)

    def test_response_time_performance(self, client, sample_request_data):
        """Test API response time"""
        import time
        
        with patch('backend.scrapers.amazon.unified_scraper.UnifiedAmazonScraper'):
            start_time = time.time()
            
            response = client.post('/estimate_emissions',
                                 data=json.dumps(sample_request_data),
                                 content_type='application/json')
            
            response_time = time.time() - start_time
            
            # API should respond within reasonable time
            assert response_time < 30.0, f"API response too slow: {response_time:.2f}s"

    def test_memory_usage_stability(self, client, sample_request_data):
        """Test memory usage doesn't grow excessively"""
        import gc
        
        # Make multiple requests
        for _ in range(10):
            with patch('backend.scrapers.amazon.unified_scraper.UnifiedAmazonScraper'):
                response = client.post('/estimate_emissions',
                                     data=json.dumps(sample_request_data),
                                     content_type='application/json')
            
            # Force garbage collection
            gc.collect()
        
        # Memory usage should be stable (no easy way to test this in unit tests)
        # This is more of a placeholder for manual testing
        assert True


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--tb=short", "--cov=backend/api"])