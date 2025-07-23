#!/usr/bin/env python3
# Initialize enterprise components for testing

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def initialize_components():
    """Initialize all enterprise components"""
    
    print("🚀 Initializing enterprise components...")
    
    # Initialize error handling
    try:
        from backend.core.exceptions import error_handler
        print("✅ Error handling framework initialized")
    except ImportError as e:
        print(f"❌ Error handling import failed: {e}")
    
    # Initialize monitoring
    try:
        from backend.core.monitoring import monitoring
        print("✅ Monitoring system initialized")
    except ImportError as e:
        print(f"❌ Monitoring import failed: {e}")
    
    # Initialize caching
    try:
        from backend.core.caching import cache
        print("✅ Caching system initialized")
    except ImportError as e:
        print(f"❌ Caching import failed: {e}")
    
    # Initialize rate limiting
    try:
        from backend.core.rate_limiting import rate_limit_service
        print("✅ Rate limiting initialized")
    except ImportError as e:
        print(f"❌ Rate limiting import failed: {e}")
    
    # Initialize API docs
    try:
        from backend.core.api_documentation import api_docs
        print("✅ API documentation initialized")
    except ImportError as e:
        print(f"❌ API documentation import failed: {e}")
    
    # Initialize ML monitoring
    try:
        from backend.core.ml_monitoring import ml_monitoring
        print("✅ ML monitoring initialized")
    except ImportError as e:
        print(f"❌ ML monitoring import failed: {e}")
    
    print("🎯 Component initialization complete!")

if __name__ == "__main__":
    initialize_components()
