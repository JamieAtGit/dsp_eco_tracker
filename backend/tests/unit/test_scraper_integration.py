#!/usr/bin/env python3
"""
Integration tests for the cleaned up scraper system
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from backend.scrapers.amazon.unified_scraper import UnifiedProductScraper, scrape_amazon_product_page

@pytest.mark.integration
class TestScraperIntegration:
    """Test the integrated scraper system"""
    
    def test_unified_scraper_initialization(self):
        """Test that unified scraper initializes correctly"""
        scraper = UnifiedProductScraper()
        
        # Should have at least 2 strategies (requests + fallback)
        assert len(scraper.strategies) >= 2
        assert scraper.cache_ttl > 0
        assert isinstance(scraper.cache, dict)
    
    def test_legacy_function_compatibility(self):
        """Test that legacy function still works"""
        test_url = "https://www.amazon.co.uk/dp/B123TEST"
        
        result = scrape_amazon_product_page(test_url)
        
        # Should return a dictionary
        assert isinstance(result, dict)
        
        # Should have expected keys
        required_keys = [
            'title', 'origin', 'weight_kg', 'material_type', 
            'brand', 'asin', 'quality_score'
        ]
        
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_scraper_error_handling(self):
        """Test that scraper handles invalid URLs gracefully"""
        scraper = UnifiedProductScraper()
        
        # Should not crash on invalid URL
        result = scraper.scrape("https://not-amazon.com/invalid")
        
        # Should return a result (fallback)
        assert result is not None
        assert hasattr(result, 'title')
        assert hasattr(result, 'quality_score')
    
    @pytest.mark.slow
    def test_real_amazon_url(self):
        """Test with a real Amazon URL (marked as slow)"""
        scraper = UnifiedProductScraper()
        test_url = "https://www.amazon.co.uk/dp/B0CL5KNB9M"
        
        result = scraper.scrape(test_url)
        
        # Should extract ASIN correctly
        assert result.asin == "B0CL5KNB9M"
        
        # Should have some quality score
        assert result.quality_score >= 0
        assert result.quality_score <= 100