#!/usr/bin/env python3
"""
🧪 DSP Eco Tracker Testing Suite
===============================

Comprehensive testing framework for the DSP Eco Tracker system.
Includes unit tests, integration tests, performance benchmarks,
and continuous integration support.

Test Structure:
- unit/: Unit tests for individual components
- integration/: Integration tests for system interactions  
- performance/: Performance and load testing
- fixtures/: Test data and mock objects
- conftest.py: Pytest configuration and shared fixtures

Usage:
    # Run all tests
    pytest

    # Run with coverage
    pytest --cov=backend --cov-report=html

    # Run specific test category
    pytest backend/tests/unit/
    pytest backend/tests/integration/

    # Run performance tests
    pytest backend/tests/performance/ -m performance
"""

__version__ = "1.0.0"
__author__ = "DSP Eco Tracker Team"