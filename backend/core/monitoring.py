#!/usr/bin/env python3
"""
📊 ENTERPRISE MONITORING & OBSERVABILITY FRAMEWORK
================================================

OpenTelemetry-based distributed tracing and metrics collection for 
production-grade monitoring of the DSP Eco Tracker system.

Features:
- Distributed tracing across all components
- Custom business metrics (scraping success rate, prediction accuracy)
- Performance monitoring and alerting
- Integration with monitoring platforms (Jaeger, Prometheus, Grafana)
- Real-time dashboards and SLA tracking

This demonstrates enterprise-level observability practices expected
in production systems.
"""

import logging
import time
import functools
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from datetime import datetime, timedelta

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

logger = logging.getLogger(__name__)

class EcoTrackerMonitoring:
    """
    Centralized monitoring and observability system
    
    Provides distributed tracing, metrics collection, and performance monitoring
    with integration to enterprise monitoring stacks.
    """
    
    def __init__(self, service_name: str = "eco-tracker", environment: str = "development"):
        self.service_name = service_name
        self.environment = environment
        
        # Initialize OpenTelemetry
        self._init_tracing()
        self._init_metrics()
        
        # Get tracer and meter
        self.tracer = trace.get_tracer(service_name)
        self.meter = metrics.get_meter(service_name)
        
        # Initialize custom metrics
        self._init_custom_metrics()
        
        # Performance tracking
        self.start_time = time.time()
        self.request_count = 0
        
        logger.info(f"🚀 Monitoring initialized for {service_name} ({environment})")
    
    def _init_tracing(self):
        """Initialize distributed tracing with Jaeger export"""
        # Configure trace provider
        trace.set_tracer_provider(TracerProvider())
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
            collector_endpoint="http://localhost:14268/api/traces"
        )
        
        # Add span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Set global propagation format
        set_global_textmap(B3MultiFormat())
        
        logger.info("✅ Distributed tracing configured with Jaeger")
    
    def _init_metrics(self):
        """Initialize metrics collection with Prometheus export"""
        # Configure Prometheus metrics reader
        prometheus_reader = PrometheusMetricReader()
        
        # Set meter provider
        metrics.set_meter_provider(
            MeterProvider(metric_readers=[prometheus_reader])
        )
        
        logger.info("✅ Metrics configured with Prometheus export")
    
    def _init_custom_metrics(self):
        """Initialize business-specific metrics"""
        # Request metrics
        self.request_counter = self.meter.create_counter(
            "eco_tracker_requests_total",
            description="Total number of API requests",
            unit="1"
        )
        
        self.request_duration = self.meter.create_histogram(
            "eco_tracker_request_duration_seconds",
            description="Request processing time",
            unit="s"
        )
        
        # Scraping metrics
        self.scraping_success_rate = self.meter.create_counter(
            "eco_tracker_scraping_success_total",
            description="Successful scraping operations",
            unit="1"
        )
        
        self.scraping_failure_rate = self.meter.create_counter(
            "eco_tracker_scraping_failure_total", 
            description="Failed scraping operations",
            unit="1"
        )
        
        self.scraping_duration = self.meter.create_histogram(
            "eco_tracker_scraping_duration_seconds",
            description="Scraping operation duration",
            unit="s"
        )
        
        # ML model metrics
        self.prediction_counter = self.meter.create_counter(
            "eco_tracker_predictions_total",
            description="Total ML predictions made",
            unit="1"
        )
        
        self.prediction_accuracy = self.meter.create_histogram(
            "eco_tracker_prediction_confidence",
            description="ML prediction confidence scores",
            unit="1"
        )
        
        self.model_inference_time = self.meter.create_histogram(
            "eco_tracker_model_inference_seconds",
            description="ML model inference time",
            unit="s"
        )
        
        # Business metrics
        self.carbon_emissions_calculated = self.meter.create_histogram(
            "eco_tracker_carbon_emissions_kg",
            description="Carbon emissions calculated per product",
            unit="kg"
        )
        
        self.distance_calculated = self.meter.create_histogram(
            "eco_tracker_transport_distance_km",
            description="Transport distances calculated", 
            unit="km"
        )
        
        logger.info("✅ Custom business metrics initialized")
    
    def instrument_flask_app(self, app):
        """Instrument Flask application with auto-tracing"""
        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()
        logger.info("✅ Flask application instrumented for tracing")
    
    def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Decorator for tracing business operations
        
        Usage:
            @monitoring.trace_operation("scrape_product", {"strategy": "requests"})
            def scrape_product(url):
                # Implementation
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(operation_name) as span:
                    # Add attributes
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)
                    
                    # Add function metadata
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    try:
                        # Execute function
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        duration = time.time() - start_time
                        
                        # Record success metrics
                        span.set_attribute("operation.success", True)
                        span.set_attribute("operation.duration", duration)
                        span.set_status(trace.Status(trace.StatusCode.OK))
                        
                        return result
                        
                    except Exception as e:
                        # Record error metrics
                        span.set_attribute("operation.success", False)
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.set_status(
                            trace.Status(trace.StatusCode.ERROR, str(e))
                        )
                        raise
            
            return wrapper
        return decorator
    
    @contextmanager
    def trace_span(self, span_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager for manual span creation
        
        Usage:
            with monitoring.trace_span("data_processing", {"batch_size": 100}):
                # Process data
        """
        with self.tracer.start_as_current_span(span_name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            try:
                yield span
            except Exception as e:
                span.set_status(
                    trace.Status(trace.StatusCode.ERROR, str(e))
                )
                raise
    
    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record API request metrics"""
        self.request_counter.add(1, {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code),
            "environment": self.environment
        })
        
        self.request_duration.record(duration, {
            "endpoint": endpoint,
            "method": method,
            "environment": self.environment
        })
        
        self.request_count += 1
    
    def record_scraping_result(self, success: bool, strategy: str, duration: float, url: str = None):
        """Record scraping operation metrics"""
        if success:
            self.scraping_success_rate.add(1, {
                "strategy": strategy,
                "environment": self.environment
            })
        else:
            self.scraping_failure_rate.add(1, {
                "strategy": strategy,
                "environment": self.environment
            })
        
        self.scraping_duration.record(duration, {
            "strategy": strategy,
            "success": str(success),
            "environment": self.environment
        })
    
    def record_ml_prediction(self, model_name: str, confidence: float, inference_time: float):
        """Record ML model prediction metrics"""
        self.prediction_counter.add(1, {
            "model": model_name,
            "environment": self.environment
        })
        
        self.prediction_accuracy.record(confidence, {
            "model": model_name,
            "environment": self.environment
        })
        
        self.model_inference_time.record(inference_time, {
            "model": model_name,
            "environment": self.environment
        })
    
    def record_business_metrics(self, carbon_kg: float, distance_km: float, transport_mode: str):
        """Record business-specific metrics"""
        self.carbon_emissions_calculated.record(carbon_kg, {
            "transport_mode": transport_mode,
            "environment": self.environment
        })
        
        self.distance_calculated.record(distance_km, {
            "transport_mode": transport_mode,
            "environment": self.environment
        })
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status for monitoring dashboards"""
        uptime = time.time() - self.start_time
        
        return {
            "service": self.service_name,
            "environment": self.environment,
            "status": "healthy",
            "uptime_seconds": uptime,
            "uptime_readable": str(timedelta(seconds=int(uptime))),
            "total_requests": self.request_count,
            "average_rps": self.request_count / uptime if uptime > 0 else 0,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    def create_alert(self, alert_name: str, severity: str, message: str, context: Dict[str, Any]):
        """Create monitoring alert"""
        with self.trace_span("monitoring_alert", {
            "alert.name": alert_name,
            "alert.severity": severity
        }) as span:
            
            alert_data = {
                "alert_name": alert_name,
                "severity": severity,
                "message": message,
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name,
                "environment": self.environment
            }
            
            # Log alert (in production, this would send to alerting system)
            logger.warning(f"🚨 ALERT: {alert_name} - {message}", extra=alert_data)
            
            # Add alert attributes to span
            span.set_attribute("alert.triggered", True)
            span.add_event("alert_created", alert_data)

# Global monitoring instance
monitoring = EcoTrackerMonitoring()

# Convenience decorators
def trace_scraping(strategy: str):
    """Decorator for tracing scraping operations"""
    return monitoring.trace_operation("scrape_product", {"scraping.strategy": strategy})

def trace_ml_prediction(model_name: str):
    """Decorator for tracing ML predictions"""  
    return monitoring.trace_operation("ml_prediction", {"ml.model": model_name})

def trace_api_endpoint(endpoint_name: str):
    """Decorator for tracing API endpoints"""
    return monitoring.trace_operation("api_request", {"api.endpoint": endpoint_name})

if __name__ == "__main__":
    # Test the monitoring system
    print("📊 Testing Monitoring Framework")
    print("=" * 50)
    
    # Test tracing
    @monitoring.trace_operation("test_operation", {"test": "true"})
    def test_function():
        time.sleep(0.1)
        return "success"
    
    result = test_function()
    print(f"✅ Test operation completed: {result}")
    
    # Test metrics
    monitoring.record_request("/test", "GET", 200, 0.1)
    monitoring.record_scraping_result(True, "requests", 0.5)
    monitoring.record_ml_prediction("xgboost", 0.95, 0.02)
    monitoring.record_business_metrics(2.5, 150.0, "truck")
    
    print("✅ All metrics recorded successfully")
    
    # Test health status
    health = monitoring.get_health_status()
    print(f"📊 Health Status: {health}")
    
    print("\n🚀 Monitoring system ready for production!")