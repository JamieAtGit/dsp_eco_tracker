#!/usr/bin/env python3
"""
⚙️ ENTERPRISE TESTING SETUP SCRIPT
==================================

Sets up the environment and dependencies needed to test all enterprise features.
This script ensures all components are properly configured and ready for testing.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_testing_environment():
    """Set up the complete testing environment"""
    
    print("⚙️ ENTERPRISE TESTING SETUP")
    print("=" * 50)
    
    # Step 1: Install required dependencies
    print("1️⃣ Installing additional testing dependencies...")
    
    additional_deps = [
        "redis",
        "opentelemetry-api",
        "opentelemetry-sdk", 
        "opentelemetry-instrumentation-flask",
        "opentelemetry-instrumentation-requests",
        "opentelemetry-exporter-jaeger-thrift",
        "opentelemetry-exporter-prometheus",
        "marshmallow",
        "pyjwt",
        "locust",
        "testcontainers",
        "scipy"
    ]
    
    for dep in additional_deps:
        try:
            print(f"   Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"   ✅ {dep} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Failed to install {dep}: {e}")
    
    # Step 2: Create configuration files
    print("\n2️⃣ Creating configuration files...")
    
    # Create environment file
    env_content = """# Enterprise Features Environment Configuration
FLASK_SECRET_KEY=your-super-secret-key-change-in-production
REDIS_URL=redis://localhost:6379
JAEGER_ENDPOINT=http://localhost:14268/api/traces
OPENTELEMETRY_SERVICE_NAME=eco-tracker
ENVIRONMENT=development
LOG_LEVEL=INFO
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("   ✅ .env file created")
    
    # Create Redis configuration
    redis_conf = """# Redis configuration for testing
port 6379
bind 127.0.0.1
save 900 1
save 300 10
save 60 10000
rdbcompression yes
dbfilename dump.rdb
dir ./
maxmemory 128mb
maxmemory-policy allkeys-lru
"""
    
    with open("redis.conf", "w") as f:
        f.write(redis_conf)
    print("   ✅ redis.conf created")
    
    # Step 3: Start Redis server
    print("\n3️⃣ Starting Redis server...")
    
    try:
        # Check if Redis is already running
        result = subprocess.run(["redis-cli", "ping"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ Redis is already running")
        else:
            raise subprocess.CalledProcessError(1, "redis-cli ping")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        try:
            print("   Starting Redis server...")
            # Start Redis in background
            subprocess.Popen(["redis-server", "redis.conf"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            time.sleep(2)  # Give Redis time to start
            
            # Verify Redis is running
            result = subprocess.run(["redis-cli", "ping"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ Redis server started successfully")
            else:
                print("   ⚠️ Redis may not be running properly")
        except FileNotFoundError:
            print("   ❌ Redis not found. Please install Redis:")
            print("      macOS: brew install redis")
            print("      Ubuntu: sudo apt-get install redis-server")
            print("      Windows: Download from https://redis.io/download")
    
    # Step 4: Create test initialization script
    print("\n4️⃣ Creating test initialization script...")
    
    init_script = """#!/usr/bin/env python3
# Initialize enterprise components for testing

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def initialize_components():
    \"\"\"Initialize all enterprise components\"\"\"
    
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
"""
    
    with open("init_enterprise_components.py", "w") as f:
        f.write(init_script)
    print("   ✅ Component initialization script created")
    
    # Step 5: Create quick test script
    print("\n5️⃣ Creating quick validation script...")
    
    quick_test = """#!/usr/bin/env python3
# Quick validation of enterprise components

import asyncio
import sys

async def quick_validation():
    \"\"\"Quick validation of all components\"\"\"
    
    print("⚡ QUICK ENTERPRISE COMPONENTS VALIDATION")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Error handling
    try:
        from backend.core.exceptions import ScrapingException
        raise ScrapingException("Test error")
    except ScrapingException as e:
        results["error_handling"] = "✅ Working"
        print(f"✅ Error handling: Exception ID {e.exception_id}")
    except Exception as e:
        results["error_handling"] = f"❌ Failed: {e}"
        print(f"❌ Error handling failed: {e}")
    
    # Test 2: Monitoring
    try:
        from backend.core.monitoring import monitoring
        health = monitoring.get_health_status()
        results["monitoring"] = "✅ Working" 
        print(f"✅ Monitoring: Service {health['service']} running")
    except Exception as e:
        results["monitoring"] = f"❌ Failed: {e}"
        print(f"❌ Monitoring failed: {e}")
    
    # Test 3: Caching
    try:
        from backend.core.caching import cache
        await cache.set("test", "value", ttl=10)
        value = await cache.get("test")
        results["caching"] = "✅ Working" if value == "value" else "⚠️ Partial"
        print(f"✅ Caching: {'Working' if value == 'value' else 'Partial (Redis may be down)'}")
    except Exception as e:
        results["caching"] = f"❌ Failed: {e}"
        print(f"❌ Caching failed: {e}")
    
    # Test 4: Rate limiting
    try:
        from backend.core.rate_limiting import UserRole, RateLimitService
        import redis.asyncio as redis
        redis_client = redis.Redis.from_url("redis://localhost:6379", decode_responses=True)
        service = RateLimitService(redis_client)
        limits = service.get_rate_limits_for_role(UserRole.PREMIUM)
        results["rate_limiting"] = "✅ Working"
        print(f"✅ Rate limiting: Premium limits = {limits['requests_per_minute']}/min")
        await redis_client.close()
    except Exception as e:
        results["rate_limiting"] = f"❌ Failed: {e}"
        print(f"❌ Rate limiting failed: {e}")
    
    # Test 5: API docs
    try:
        from backend.core.api_documentation import api_docs
        spec = api_docs.generate_openapi_spec()
        results["api_docs"] = "✅ Working"
        print(f"✅ API docs: {spec['info']['title']} v{spec['info']['version']}")
    except Exception as e:
        results["api_docs"] = f"❌ Failed: {e}"
        print(f"❌ API docs failed: {e}")
    
    # Test 6: ML monitoring
    try:
        from backend.core.ml_monitoring import MLMonitoringService
        monitor = MLMonitoringService("test", "1.0")
        results["ml_monitoring"] = "✅ Working"
        print(f"✅ ML monitoring: Service initialized for {monitor.model_name}")
    except Exception as e:
        results["ml_monitoring"] = f"❌ Failed: {e}"
        print(f"❌ ML monitoring failed: {e}")
    
    print("\\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    working = sum(1 for v in results.values() if v == "✅ Working")
    total = len(results)
    
    print(f"✅ Working: {working}/{total} components")
    
    if working == total:
        print("🏆 All enterprise components are ready!")
        print("🚀 You can now run: python test_enterprise_features.py")
    elif working >= total * 0.8:
        print("🎯 Most components working - ready for testing")
        print("🚀 You can run: python test_enterprise_features.py")
    else:
        print("⚠️ Several components have issues - check dependencies")
        print("💡 Try: pip install -r requirements.txt")
    
    return results

if __name__ == "__main__":
    asyncio.run(quick_validation())
"""
    
    with open("quick_validate_enterprise.py", "w") as f:
        f.write(quick_test)
    print("   ✅ Quick validation script created")
    
    # Step 6: Create requirements file for enterprise features
    print("\n6️⃣ Creating enterprise requirements file...")
    
    enterprise_requirements = """# Enterprise Features Requirements
# Core ML and Data Science
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
scipy>=1.7.0
joblib>=1.1.0

# Web Framework
flask>=2.0.0
flask-cors>=3.0.0

# Async and Redis
redis>=4.0.0
aioredis>=2.0.0

# OpenTelemetry (Monitoring)
opentelemetry-api>=1.15.0
opentelemetry-sdk>=1.15.0
opentelemetry-instrumentation-flask>=0.36b0
opentelemetry-instrumentation-requests>=0.36b0
opentelemetry-exporter-jaeger-thrift>=1.15.0
opentelemetry-exporter-prometheus>=1.12.0rc1

# Authentication and Security
pyjwt>=2.4.0
marshmallow>=3.14.0

# Testing and Development
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
locust>=2.0.0
testcontainers>=3.4.0

# Optional: For advanced features
psycopg2-binary>=2.9.0  # PostgreSQL support
sqlalchemy>=1.4.0       # Database ORM
alembic>=1.8.0          # Database migrations
"""
    
    with open("requirements-enterprise.txt", "w") as f:
        f.write(enterprise_requirements)
    print("   ✅ Enterprise requirements file created")
    
    print("\n" + "=" * 50)
    print("🎯 SETUP COMPLETE!")
    print("=" * 50)
    print("Next steps:")
    print("1️⃣ Run quick validation: python quick_validate_enterprise.py")
    print("2️⃣ Run full test suite: python test_enterprise_features.py")
    print("3️⃣ Check test results in: enterprise_test_results.json")
    print("\n🚀 Your enterprise features are ready for testing!")

if __name__ == "__main__":
    setup_testing_environment()