#!/usr/bin/env python3
"""
🏗️ DSP Eco Tracker Core Module
=============================

Core infrastructure components for the DSP Eco Tracker system:
- Exception handling and error management
- Logging configuration
- Data validation frameworks
- Common utilities and constants

This module provides the foundational infrastructure that all other
components depend on for reliable, production-grade operation.
"""

from .exceptions import (
    BaseEcoTrackerException,
    ScrapingException,
    DataValidationException,
    MLModelException,
    ConfigurationException,
    RateLimitException,
    ErrorHandler,
    ErrorSeverity,
    ErrorCategory,
    error_handler,
    handle_scraping_error,
    validate_input_data
)

__version__ = "1.0.0"
__author__ = "DSP Eco Tracker Team"

__all__ = [
    "BaseEcoTrackerException",
    "ScrapingException", 
    "DataValidationException",
    "MLModelException",
    "ConfigurationException",
    "RateLimitException",
    "ErrorHandler",
    "ErrorSeverity",
    "ErrorCategory",
    "error_handler",
    "handle_scraping_error",
    "validate_input_data"
]