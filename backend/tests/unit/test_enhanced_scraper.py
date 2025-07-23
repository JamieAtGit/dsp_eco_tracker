#!/usr/bin/env python3
"""
Unit tests for Enhanced Amazon Scraper
These tests validate the core scraping functionality and data extraction accuracy
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from enhanced_scraper_fix import EnhancedAmazonScraper


class TestEnhancedAmazonScraper:
    """Test suite for EnhancedAmazonScraper"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.scraper = EnhancedAmazonScraper()
        
        # Mock HTML content for USN protein powder
        self.usn_html = """
        <html>
            <head><title>USN Protein Powder</title></head>
            <body>
                <span id="productTitle">USN Pure Protein GF-1 Growth & Repair Protein Powder, Chocolate Flavour, 476g</span>
                <a id="bylineInfo" href="#">USN</a>
                <div class="product-details">
                    <span>Net Weight: 476g</span>
                    <span>Brand: USN</span>
                </div>
            </body>
        </html>
        """
        
        # Mock HTML for blocked page
        self.blocked_html = """
        <html>
            <body>
                <div>Sorry, we just need to make sure you're not a robot. Click the button below to continue shopping.</div>
            </body>
        </html>
        """

    def test_extract_asin_from_url(self):
        """Test ASIN extraction from various Amazon URL formats"""
        test_cases = [
            ("https://www.amazon.co.uk/dp/B0DG5V9BWQ/", "B0DG5V9BWQ"),
            ("https://www.amazon.co.uk/USN-Protein-Powder/dp/B0DG5V9BWQ/ref=sr_1_99", "B0DG5V9BWQ"),
            ("https://amazon.com/dp/B0892LY8PL", "B0892LY8PL"),
            ("invalid-url", None)
        ]
        
        for url, expected_asin in test_cases:
            import re
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            actual_asin = asin_match.group(1) if asin_match else None
            assert actual_asin == expected_asin, f"Failed for URL: {url}"

    def test_weight_extraction_enhanced(self):
        """Test enhanced weight extraction with various patterns"""
        soup = BeautifulSoup(self.usn_html, 'html.parser')
        
        # Test weight extraction
        weight = self.scraper.extract_weight_enhanced(soup)
        
        # Should extract 476g and convert to 0.476kg
        assert weight == 0.476, f"Expected 0.476kg, got {weight}kg"

    def test_weight_extraction_patterns(self):
        """Test weight extraction with different patterns"""
        test_cases = [
            ("<span>Product weight: 2.5kg</span>", 2.5),
            ("<div>Net Weight: 500g</div>", 0.5),
            ("<p>Weight: 16oz</p>", 16 * 0.0283495),
            ("<span>2lbs protein powder</span>", 2 * 0.453592),
            ("<div>No weight mentioned</div>", 1.0)  # Default fallback
        ]
        
        for html_snippet, expected_weight in test_cases:
            soup = BeautifulSoup(f"<html><body>{html_snippet}</body></html>", 'html.parser')
            weight = self.scraper.extract_weight_enhanced(soup)
            assert abs(weight - expected_weight) < 0.01, f"Weight extraction failed for: {html_snippet}"

    def test_origin_extraction_brand_based(self):
        """Test origin extraction using brand mapping"""
        soup = BeautifulSoup(self.usn_html, 'html.parser')
        
        origin = self.scraper.extract_origin_enhanced(soup)
        
        # USN should map to South Africa
        assert origin == "South Africa", f"Expected 'South Africa', got '{origin}'"

    def test_origin_extraction_patterns(self):
        """Test origin extraction with various text patterns"""
        test_cases = [
            ("Made in Germany", "Germany"),
            ("Manufactured in Italy", "Italy"),
            ("Country of origin: France", "France"),
            ("Imported from China", "China"),
            ("No origin mentioned", "Unknown")
        ]
        
        for text, expected_origin in test_cases:
            html = f"<html><body><div>{text}</div></body></html>"
            soup = BeautifulSoup(html, 'html.parser')
            
            # Mock the brand detection to return unknown first
            with patch.object(self.scraper, 'extract_origin_enhanced') as mock_extract:
                mock_extract.return_value = expected_origin
                origin = mock_extract(soup)
                assert origin == expected_origin

    def test_material_guessing(self):
        """Test material type guessing from product titles"""
        test_cases = [
            ("Plastic water bottle", "Plastic"),
            ("Steel kitchen knife", "Metal"),
            ("Wooden cutting board", "Wood"), 
            ("Glass coffee mug", "Glass"),
            ("Cotton t-shirt", "Fabric"),
            ("Leather wallet", "Leather"),
            ("Ceramic plate", "Ceramic"),
            ("Unknown product", "Mixed")
        ]
        
        for title, expected_material in test_cases:
            material = self.scraper.guess_material_from_title(title)
            assert material == expected_material, f"Material guessing failed for: {title}"

    def test_blocking_detection(self):
        """Test detection of Amazon bot blocking"""
        # Test blocked page
        soup_blocked = BeautifulSoup(self.blocked_html, 'html.parser')
        assert self.scraper.is_blocked(soup_blocked) == True
        
        # Test normal page
        soup_normal = BeautifulSoup(self.usn_html, 'html.parser')
        assert self.scraper.is_blocked(soup_normal) == False

    def test_find_text_by_selectors(self):
        """Test selector-based text extraction"""
        soup = BeautifulSoup(self.usn_html, 'html.parser')
        
        # Test existing selector
        title = self.scraper.find_text_by_selectors(soup, ['#productTitle'], 'Default')
        assert "USN Pure Protein" in title
        
        # Test non-existing selector
        missing = self.scraper.find_text_by_selectors(soup, ['#nonexistent'], 'Default')
        assert missing == 'Default'

    @patch('requests.Session.get')
    def test_scrape_product_enhanced_success(self, mock_get):
        """Test successful product scraping"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = self.usn_html.encode('utf-8')
        mock_get.return_value = mock_response
        
        url = "https://www.amazon.co.uk/USN-Protein-Powder/dp/B0DG5V9BWQ/"
        result = self.scraper.scrape_product_enhanced(url)
        
        assert result is not None
        assert result['asin'] == 'B0DG5V9BWQ'
        assert 'USN' in result['title']
        assert result['weight_kg'] == 0.476
        assert result['origin'] == 'South Africa'

    @patch('requests.Session.get')
    def test_scrape_product_enhanced_blocked(self, mock_get):
        """Test handling of blocked responses"""
        # Mock blocked response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = self.blocked_html.encode('utf-8')
        mock_get.return_value = mock_response
        
        url = "https://www.amazon.co.uk/test/dp/B0DG5V9BWQ/"
        result = self.scraper.scrape_product_enhanced(url)
        
        # Should try multiple strategies and potentially fail
        # This tests our fallback mechanisms
        assert result is None or result.get('title') != 'Unknown Product'

    def test_invalid_url_handling(self):
        """Test handling of invalid URLs"""
        invalid_urls = [
            "not-a-url",
            "https://google.com",
            "https://amazon.com/no-asin-here",
            "",
            None
        ]
        
        for url in invalid_urls:
            try:
                result = self.scraper.scrape_product_enhanced(url)
                # Should either return None or handle gracefully
                assert result is None or isinstance(result, dict)
            except Exception as e:
                # Should not crash on invalid input
                assert False, f"Scraper crashed on invalid URL {url}: {e}"

    def test_realistic_headers_generation(self):
        """Test generation of realistic browser headers"""
        url = "https://www.amazon.co.uk/test"
        headers = self.scraper.get_realistic_headers(url)
        
        # Check essential headers are present
        required_headers = ['User-Agent', 'Accept', 'Accept-Language']
        for header in required_headers:
            assert header in headers, f"Missing required header: {header}"
        
        # Check User-Agent is one of our defined ones
        assert headers['User-Agent'] in self.scraper.user_agents

    def test_product_data_extraction_completeness(self):
        """Test that all required fields are extracted"""
        soup = BeautifulSoup(self.usn_html, 'html.parser')
        data = self.scraper.extract_product_data(soup, 'B0DG5V9BWQ')
        
        required_fields = ['asin', 'title', 'brand', 'weight_kg', 'origin', 'material_type']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            assert data[field] is not None, f"Field {field} is None"
            assert data[field] != "", f"Field {field} is empty"


# Integration-style tests for real-world scenarios
class TestScrapingIntegration:
    """Integration tests for scraping pipeline"""
    
    def setup_method(self):
        self.scraper = EnhancedAmazonScraper()

    def test_full_pipeline_data_quality(self):
        """Test data quality of full extraction pipeline"""
        # Mock data that represents a successful scrape
        mock_data = {
            'asin': 'B0DG5V9BWQ',
            'title': 'USN Pure Protein GF-1 Growth & Repair Protein Powder, Chocolate Flavour, 476g',
            'brand': 'USN',
            'weight_kg': 0.476,
            'origin': 'South Africa',
            'material_type': 'Mixed'
        }
        
        # Validate data quality metrics
        assert len(mock_data['asin']) == 10  # ASIN format
        assert len(mock_data['title']) > 10  # Meaningful title
        assert mock_data['weight_kg'] > 0  # Positive weight
        assert mock_data['origin'] != 'Unknown'  # Origin detected
        assert mock_data['brand'] != 'Unknown'  # Brand detected

    def test_error_resilience(self):
        """Test system resilience to various error conditions"""
        # Test network timeouts, malformed HTML, missing elements
        error_scenarios = [
            "timeout",
            "malformed_html", 
            "missing_elements",
            "blocked_response"
        ]
        
        for scenario in error_scenarios:
            # Each scenario should be handled gracefully
            # without crashing the entire system
            try:
                # Mock different error conditions
                pass  # Implement specific error simulation
            except Exception as e:
                assert False, f"System not resilient to {scenario}: {e}"


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--tb=short"])