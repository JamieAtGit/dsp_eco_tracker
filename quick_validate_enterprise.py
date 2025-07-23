#!/usr/bin/env python3
# Quick validation of enterprise components

import asyncio
import sys

async def quick_validation():
    """Quick validation of all components"""
    
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
    
    print("\n" + "=" * 50)
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
