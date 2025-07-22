#!/usr/bin/env python3
"""
🧪 Unit Tests: Unified Scraper
=============================

Comprehensive unit tests for the unified scraping system.
Tests individual components in isolation with mocked dependencies.

Coverage:
- ScrapingResult data class
- Strategy pattern implementation
- Error handling and exceptions
- Quality assessment logic
- Caching mechanisms
- Input validation
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from backend.scrapers.amazon.unified_scraper import (
    UnifiedProductScraper,
    ScrapingResult,
    ConfidenceLevel,
    ScrapingStrategy,
    RequestsStrategy,
    FallbackStrategy,
    ScrapingStrategyBase
)
from backend.core.exceptions import (
    ScrapingException,
    DataValidationException,
    ErrorSeverity,
    ErrorCategory
)

@pytest.mark.unit
class TestScrapingResult:
    """Test the ScrapingResult data class"""
    
    def test_scraping_result_creation(self):
        """Test basic ScrapingResult creation"""
        result = ScrapingResult(
            title="Test Product",
            origin="UK",
            weight_kg=1.5,
            dimensions_cm=[20, 15, 10],
            material_type="Plastic",
            recyclability="High",
            brand="TestBrand",
            asin="B123456789",
            quality_score=85,
            confidence_level=ConfidenceLevel.HIGH
        )
        
        assert result.title == "Test Product"
        assert result.origin == "UK"
        assert result.weight_kg == 1.5
        assert result.quality_score == 85
        assert result.confidence_level == ConfidenceLevel.HIGH
        
    def test_scraping_result_defaults(self):
        """Test default values are properly initialized"""
        result = ScrapingResult(
            title="Test",
            origin="UK", 
            weight_kg=1.0,
            dimensions_cm=[10, 10, 10],
            material_type="Unknown",
            recyclability="Medium",
            brand="Unknown",
            asin="Unknown"
        )
        
        assert result.data_sources == {}
        assert result.errors_encountered == []
        assert result.warnings == []
        assert result.quality_score == 0
        assert result.confidence_level == ConfidenceLevel.LOW
        
    def test_is_high_quality(self):
        """Test quality assessment logic"""
        # High quality result
        high_quality = ScrapingResult(
            title="Test", origin="UK", weight_kg=1.0,
            dimensions_cm=[10, 10, 10], material_type="Plastic",
            recyclability="High", brand="Test", asin="B123",
            quality_score=85, confidence_level=ConfidenceLevel.HIGH
        )
        assert high_quality.is_high_quality() == True
        
        # Medium quality result  
        medium_quality = ScrapingResult(
            title="Test", origin="UK", weight_kg=1.0,
            dimensions_cm=[10, 10, 10], material_type="Plastic",
            recyclability="High", brand="Test", asin="B123", 
            quality_score=85, confidence_level=ConfidenceLevel.MEDIUM
        )
        assert medium_quality.is_high_quality() == True
        
        # Low quality result
        low_quality = ScrapingResult(
            title="Test", origin="UK", weight_kg=1.0,
            dimensions_cm=[10, 10, 10], material_type="Plastic",
            recyclability="High", brand="Test", asin="B123",
            quality_score=75, confidence_level=ConfidenceLevel.LOW
        )
        assert low_quality.is_high_quality() == False
        
    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        result = ScrapingResult(
            title="Test Product",
            origin="Germany",
            weight_kg=2.5,
            dimensions_cm=[25, 20, 15],
            material_type="Metal",
            recyclability="High", 
            brand="TestBrand",
            asin="B987654321"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["title"] == "Test Product"
        assert result_dict["origin"] == "Germany"
        assert result_dict["weight_kg"] == 2.5
        assert "data_sources" in result_dict
        assert "errors_encountered" in result_dict

@pytest.mark.unit 
class TestRequestsStrategy:
    """Test the RequestsStrategy implementation"""
    
    def test_can_handle_amazon_urls(self):
        """Test URL handling logic"""
        strategy = RequestsStrategy()
        
        # Valid Amazon URLs
        assert strategy.can_handle("https://www.amazon.co.uk/dp/B123") == True
        assert strategy.can_handle("https://amazon.com/product/xyz") == True
        assert strategy.can_handle("https://amazon.de/item") == True
        
        # Invalid URLs
        assert strategy.can_handle("https://google.com") == False
        assert strategy.can_handle("https://ebay.co.uk") == False
        assert strategy.can_handle("") == False
        
    def test_strategy_properties(self):
        """Test strategy metadata"""
        strategy = RequestsStrategy()
        
        assert strategy.strategy_name == ScrapingStrategy.REQUESTS
        assert strategy.priority == 0  # Highest priority
        
    @patch('backend.scrapers.amazon.unified_scraper.scrape_with_requests')
    def test_successful_scraping(self, mock_scrape, mock_product_data):
        """Test successful scraping scenario"""
        # Setup mock
        mock_scrape.return_value = mock_product_data
        
        strategy = RequestsStrategy()
        result = strategy.scrape("https://amazon.co.uk/dp/B123")
        
        # Verify result
        assert isinstance(result, ScrapingResult)
        assert result.title == mock_product_data["title"]
        assert result.origin == mock_product_data["origin"]
        assert result.weight_kg == mock_product_data["weight_kg"]
        assert result.strategy_used == ScrapingStrategy.REQUESTS
        assert result.quality_score > 0
        
        # Verify mock was called
        mock_scrape.assert_called_once_with("https://amazon.co.uk/dp/B123")
        
    @patch('backend.scrapers.amazon.unified_scraper.scrape_with_requests')
    def test_scraping_failure(self, mock_scrape):
        """Test scraping failure handling"""
        # Setup mock to return no data
        mock_scrape.return_value = {"title": "Unknown Product"}
        
        strategy = RequestsStrategy()
        
        with pytest.raises(ScrapingException) as exc_info:
            strategy.scrape("https://amazon.co.uk/dp/B123")
        
        assert exc_info.value.category == ErrorCategory.PARSING
        assert "no data" in str(exc_info.value).lower()
        
    @patch('backend.scrapers.amazon.unified_scraper.scrape_with_requests')
    def test_scraping_exception(self, mock_scrape):
        """Test handling of unexpected exceptions"""
        # Setup mock to raise exception
        mock_scrape.side_effect = ValueError("Network error")
        
        strategy = RequestsStrategy()
        
        with pytest.raises(ScrapingException) as exc_info:
            strategy.scrape("https://amazon.co.uk/dp/B123")
        
        assert exc_info.value.category == ErrorCategory.NETWORK
        assert "Network error" in str(exc_info.value)
        
    def test_quality_score_calculation(self):
        """Test quality score calculation logic"""
        strategy = RequestsStrategy()
        
        # High quality data
        high_quality_data = {
            "title": "Detailed Product Title With Many Words",
            "origin": "Germany",
            "weight_kg": 2.5,
            "brand": "Known Brand",
            "material_type": "Plastic"
        }
        score = strategy._calculate_quality_score(high_quality_data)
        assert score >= 80
        
        # Low quality data
        low_quality_data = {
            "title": "Unknown",
            "origin": "Unknown", 
            "weight_kg": 1.0,  # Default
            "brand": "Unknown",
            "material_type": "Unknown"
        }
        score = strategy._calculate_quality_score(low_quality_data)
        assert score < 50
        
    def test_confidence_level_determination(self):
        """Test confidence level mapping"""
        strategy = RequestsStrategy()
        
        # Test different quality scores
        high_quality = {"title": "Good Title", "origin": "UK", "weight_kg": 2.0, "brand": "Brand", "material_type": "Metal"}
        assert strategy._determine_confidence_level(high_quality) == ConfidenceLevel.HIGH
        
        medium_quality = {"title": "Title", "origin": "UK", "weight_kg": 1.0, "brand": "Unknown", "material_type": "Unknown"}
        confidence = strategy._determine_confidence_level(medium_quality)
        assert confidence in [ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]

@pytest.mark.unit
class TestFallbackStrategy:
    """Test the FallbackStrategy implementation"""
    
    def test_can_handle_any_url(self):
        """Test that fallback can handle any URL"""
        strategy = FallbackStrategy()
        
        assert strategy.can_handle("https://amazon.co.uk/dp/B123") == True
        assert strategy.can_handle("https://google.com") == True
        assert strategy.can_handle("invalid-url") == True
        assert strategy.can_handle("") == True
        
    def test_strategy_properties(self):
        """Test strategy metadata"""
        strategy = FallbackStrategy()
        
        assert strategy.strategy_name == ScrapingStrategy.FALLBACK
        assert strategy.priority == 999  # Lowest priority
        
    def test_protein_product_detection(self):
        """Test protein product URL analysis"""
        strategy = FallbackStrategy()
        
        protein_url = "https://amazon.co.uk/protein-powder/dp/B123"
        result = strategy.scrape(protein_url)
        
        assert "protein" in result.title.lower()
        assert result.material_type == "Plastic"
        assert result.weight_kg == 2.0
        assert result.quality_score == 35
        assert result.confidence_level == ConfidenceLevel.MINIMAL
        
    def test_electronic_product_detection(self):
        """Test electronic product URL analysis"""
        strategy = FallbackStrategy()
        
        electronic_url = "https://amazon.co.uk/laptop-computer/dp/B123" 
        result = strategy.scrape(electronic_url)
        
        assert "electronic" in result.title.lower()
        assert result.material_type == "Mixed"
        assert result.origin == "China"
        
    def test_book_product_detection(self):
        """Test book product URL analysis"""
        strategy = FallbackStrategy()
        
        book_url = "https://amazon.co.uk/programming-book/dp/B123"
        result = strategy.scrape(book_url)
        
        assert result.title == "Book"
        assert result.material_type == "Paper"
        assert result.weight_kg == 0.3
        
    def test_asin_extraction(self):
        """Test ASIN extraction from URL"""
        strategy = FallbackStrategy()
        
        url_with_asin = "https://amazon.co.uk/product/dp/B0CKFK6716/ref=xyz"
        result = strategy.scrape(url_with_asin)
        
        assert result.asin == "B0CKFK6716"
        
    def test_fallback_warnings(self):
        """Test that fallback includes appropriate warnings"""
        strategy = FallbackStrategy()
        
        result = strategy.scrape("https://amazon.co.uk/unknown/dp/B123")
        
        assert len(result.warnings) > 0
        assert "fallback strategy" in result.warnings[0].lower()

@pytest.mark.unit
class TestUnifiedProductScraper:
    """Test the main UnifiedProductScraper class"""
    
    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = UnifiedProductScraper(cache_ttl=7200)
        
        assert len(scraper.strategies) >= 2  # At least requests + fallback
        assert scraper.cache_ttl == 7200
        assert isinstance(scraper.cache, dict)
        
        # Verify strategies are sorted by priority
        priorities = [s.priority for s in scraper.strategies]
        assert priorities == sorted(priorities)
        
    def test_input_validation(self):
        """Test input validation for scraping"""
        scraper = UnifiedProductScraper()
        
        # Invalid URLs should raise DataValidationException
        with pytest.raises(DataValidationException):
            scraper.scrape("")
            
        with pytest.raises(DataValidationException):
            scraper.scrape(None)
            
    @patch('backend.scrapers.amazon.unified_scraper.RequestsStrategy')
    def test_successful_scraping_flow(self, mock_strategy_class, mock_product_data):
        """Test complete scraping flow with mocked strategy"""
        # Setup mock strategy
        mock_strategy = Mock(spec=ScrapingStrategyBase)
        mock_strategy.can_handle.return_value = True
        mock_strategy.priority = 0
        mock_strategy.strategy_name = ScrapingStrategy.REQUESTS
        
        # Create mock result
        mock_result = ScrapingResult(
            title=mock_product_data["title"],
            origin=mock_product_data["origin"],
            weight_kg=mock_product_data["weight_kg"],
            dimensions_cm=mock_product_data["dimensions_cm"],
            material_type=mock_product_data["material_type"],
            recyclability=mock_product_data["recyclability"],
            brand=mock_product_data["brand"],
            asin=mock_product_data["asin"]
        )
        mock_strategy.scrape.return_value = mock_result
        mock_strategy_class.return_value = mock_strategy
        
        # Test scraping
        scraper = UnifiedProductScraper()
        scraper.strategies = [mock_strategy]  # Use only our mock
        
        result = scraper.scrape("https://amazon.co.uk/dp/B123")
        
        assert result == mock_result
        mock_strategy.scrape.assert_called_once_with("https://amazon.co.uk/dp/B123")
        
    def test_strategy_fallback_chain(self):
        """Test that strategies are tried in priority order"""
        # Create mock strategies that fail
        failing_strategy = Mock(spec=ScrapingStrategyBase)
        failing_strategy.can_handle.return_value = True
        failing_strategy.priority = 0
        failing_strategy.strategy_name = ScrapingStrategy.REQUESTS
        failing_strategy.scrape.side_effect = ScrapingException("Mock failure")
        
        # Create working fallback
        working_strategy = Mock(spec=ScrapingStrategyBase) 
        working_strategy.can_handle.return_value = True
        working_strategy.priority = 999
        working_strategy.strategy_name = ScrapingStrategy.FALLBACK
        mock_result = ScrapingResult(
            title="Fallback", origin="UK", weight_kg=1.0,
            dimensions_cm=[10, 10, 10], material_type="Unknown",
            recyclability="Medium", brand="Unknown", asin="Unknown"
        )
        working_strategy.scrape.return_value = mock_result
        
        scraper = UnifiedProductScraper()
        scraper.strategies = [failing_strategy, working_strategy]
        
        result = scraper.scrape("https://amazon.co.uk/dp/B123")
        
        # Verify both strategies were attempted
        failing_strategy.scrape.assert_called_once()
        working_strategy.scrape.assert_called_once()
        assert result == mock_result
        
    def test_caching_functionality(self, performance_timer):
        """Test caching mechanism"""
        scraper = UnifiedProductScraper(cache_ttl=3600)
        
        # Mock strategy for consistent results
        mock_strategy = Mock(spec=ScrapingStrategyBase)
        mock_strategy.can_handle.return_value = True
        mock_strategy.priority = 0
        mock_strategy.strategy_name = ScrapingStrategy.REQUESTS
        mock_result = ScrapingResult(
            title="Cached Product", origin="UK", weight_kg=1.0,
            dimensions_cm=[10, 10, 10], material_type="Plastic",
            recyclability="High", brand="TestBrand", asin="B123"
        )
        mock_strategy.scrape.return_value = mock_result
        scraper.strategies = [mock_strategy]
        
        url = "https://amazon.co.uk/dp/B123"
        
        # First call - should hit strategy
        performance_timer.start()
        result1 = scraper.scrape(url)
        performance_timer.stop()
        first_call_time = performance_timer.elapsed_ms
        
        # Second call - should hit cache
        performance_timer.start()
        result2 = scraper.scrape(url)
        performance_timer.stop()
        second_call_time = performance_timer.elapsed_ms
        
        # Verify results are identical
        assert result1.title == result2.title
        assert result1.asin == result2.asin
        
        # Verify strategy was only called once
        mock_strategy.scrape.assert_called_once()
        
        # Cache should be faster (though both are very fast with mocks)
        assert second_call_time <= first_call_time
        
    def test_cache_expiration(self):
        """Test cache expiration functionality"""
        scraper = UnifiedProductScraper(cache_ttl=1)  # 1 second TTL
        
        # Add item to cache manually
        test_result = ScrapingResult(
            title="Test", origin="UK", weight_kg=1.0,
            dimensions_cm=[10, 10, 10], material_type="Unknown",
            recyclability="Medium", brand="Unknown", asin="Unknown"
        )
        scraper._cache_result("https://test.com", test_result)
        
        # Should be in cache
        cached = scraper._get_cached_result("https://test.com")
        assert cached is not None
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        expired = scraper._get_cached_result("https://test.com")
        assert expired is None
        
    def test_cache_statistics(self):
        """Test cache statistics functionality"""
        scraper = UnifiedProductScraper()
        
        # Add test items
        test_result = ScrapingResult(
            title="Test", origin="UK", weight_kg=1.0,
            dimensions_cm=[10, 10, 10], material_type="Unknown",
            recyclability="Medium", brand="Unknown", asin="Unknown"
        )
        
        scraper._cache_result("https://test1.com", test_result)
        scraper._cache_result("https://test2.com", test_result)
        
        stats = scraper.get_cache_stats()
        
        assert stats["total_entries"] == 2
        assert stats["valid_entries"] == 2
        assert stats["expired_entries"] == 0
        assert "cache_ttl_hours" in stats
        
    def test_cache_clearing(self):
        """Test cache clearing functionality"""
        scraper = UnifiedProductScraper()
        
        # Add test items
        test_result = ScrapingResult(
            title="Test", origin="UK", weight_kg=1.0,
            dimensions_cm=[10, 10, 10], material_type="Unknown",
            recyclability="Medium", brand="Unknown", asin="Unknown"
        )
        
        scraper._cache_result("https://test1.com", test_result)
        scraper._cache_result("https://test2.com", test_result)
        
        # Verify items in cache
        assert len(scraper.cache) == 2
        
        # Clear cache
        cleared_count = scraper.clear_cache()
        
        assert cleared_count == 2
        assert len(scraper.cache) == 0

@pytest.mark.unit
class TestLegacyCompatibility:
    """Test backward compatibility with existing code"""
    
    @patch('backend.scrapers.amazon.unified_scraper.UnifiedProductScraper')
    def test_legacy_function_interface(self, mock_scraper_class):
        """Test legacy function maintains expected interface"""
        from backend.scrapers.amazon.unified_scraper import scrape_amazon_product_page
        
        # Setup mock
        mock_scraper = Mock()
        mock_result = ScrapingResult(
            title="Test Product",
            origin="UK",
            weight_kg=1.5,
            dimensions_cm=[20, 15, 10],
            material_type="Plastic",
            recyclability="High",
            brand="TestBrand",
            asin="B123456789"
        )
        mock_scraper.scrape.return_value = mock_result
        mock_scraper_class.return_value = mock_scraper
        
        # Test legacy function
        result = scrape_amazon_product_page("https://amazon.co.uk/dp/B123")
        
        # Verify legacy format
        assert isinstance(result, dict)
        required_legacy_fields = [
            "title", "origin", "weight_kg", "dimensions_cm",
            "material_type", "recyclability", "eco_score_ml", 
            "transport_mode", "carbon_kg"
        ]
        
        for field in required_legacy_fields:
            assert field in result
            
        # Verify enhanced fields are also present
        enhanced_fields = [
            "brand", "asin", "quality_score", "confidence_level",
            "strategy_used", "extraction_time_ms"
        ]
        
        for field in enhanced_fields:
            assert field in result
            
    def test_fallback_mode_compatibility(self):
        """Test fallback mode still works as expected"""
        from backend.scrapers.amazon.unified_scraper import scrape_amazon_product_page
        
        result = scrape_amazon_product_page("https://amazon.co.uk/dp/B123", fallback=True)
        
        assert isinstance(result, dict)
        assert "title" in result
        assert "origin" in result
        
        # Should be using fallback data
        assert "fallback" in result["title"].lower() or result["title"] == "Consumer Product"

if __name__ == "__main__":
    # Run tests with coverage
    import subprocess
    subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short",
        "--cov=backend.scrapers.amazon.unified_scraper",
        "--cov-report=term-missing"
    ])