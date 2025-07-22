#!/usr/bin/env python3
"""
🚨 PRODUCTION ERROR HANDLING FRAMEWORK
=====================================

Professional exception hierarchy with context, recovery strategies,
and comprehensive error tracking for the DSP Eco Tracker system.

Features:
- Custom exception hierarchy with specific error types
- Error context preservation for debugging
- Recovery strategy suggestions
- Error severity levels and categorization  
- Integration with logging and monitoring systems
- User-friendly error messages with technical details

Usage:
    try:
        result = risky_operation()
    except ScrapingException as e:
        logger.error(f"Scraping failed: {e}", extra=e.get_context())
        return e.get_fallback_result()
"""

import json
import traceback
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ErrorSeverity(str, Enum):
    """Error severity levels for monitoring and alerting"""
    CRITICAL = "critical"    # System failure, requires immediate attention
    HIGH = "high"           # Major functionality broken, affects core features
    MEDIUM = "medium"       # Partial functionality loss, has workarounds
    LOW = "low"            # Minor issues, doesn't affect main functionality
    INFO = "info"          # Informational, not actual errors

class ErrorCategory(str, Enum):
    """Error categories for systematic handling"""
    NETWORK = "network"          # HTTP, connection, timeout errors
    PARSING = "parsing"          # HTML parsing, data extraction errors  
    VALIDATION = "validation"    # Data validation, format errors
    AUTHENTICATION = "auth"      # Login, permissions, API key errors
    RATE_LIMIT = "rate_limit"    # Rate limiting, throttling errors
    CONFIGURATION = "config"     # Missing config, invalid settings
    DATA_QUALITY = "data_quality" # Poor quality scraped data
    EXTERNAL_API = "external_api" # Third-party API failures
    SYSTEM = "system"            # File system, memory, CPU errors
    UNKNOWN = "unknown"          # Unclassified errors

class BaseEcoTrackerException(Exception):
    """
    Base exception for all DSP Eco Tracker errors
    
    Provides comprehensive error context, recovery suggestions,
    and integration with monitoring systems.
    """
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict[str, Any]] = None,
        recovery_suggestion: Optional[str] = None,
        user_message: Optional[str] = None,
        technical_details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        
        self.message = message
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.recovery_suggestion = recovery_suggestion
        self.user_message = user_message or "An error occurred. Please try again."
        self.technical_details = technical_details or {}
        
        # Auto-generated metadata
        self.timestamp = datetime.utcnow().isoformat()
        self.exception_id = self._generate_exception_id()
        self.stack_trace = traceback.format_exc()
        
        # Log the error automatically
        self._log_error()
    
    def _generate_exception_id(self) -> str:
        """Generate unique identifier for this exception"""
        import hashlib
        content = f"{self.__class__.__name__}_{self.message}_{self.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def _log_error(self) -> None:
        """Automatically log the error with appropriate level"""
        log_level = {
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.INFO: logging.DEBUG
        }.get(self.severity, logging.WARNING)
        
        logger.log(
            log_level,
            f"[{self.exception_id}] {self.__class__.__name__}: {self.message}",
            extra=self.get_logging_context()
        )
    
    def get_context(self) -> Dict[str, Any]:
        """Get complete error context for debugging"""
        return {
            "exception_id": self.exception_id,
            "severity": self.severity,
            "category": self.category,
            "timestamp": self.timestamp,
            "context": self.context,
            "technical_details": self.technical_details,
            "recovery_suggestion": self.recovery_suggestion,
            "stack_trace": self.stack_trace
        }
    
    def get_logging_context(self) -> Dict[str, Any]:
        """Get context optimized for logging systems"""
        return {
            "exception_id": self.exception_id,
            "severity": self.severity,
            "category": self.category,
            "error_context": self.context
        }
    
    def get_user_response(self) -> Dict[str, Any]:
        """Get user-friendly error response"""
        return {
            "error": True,
            "message": self.user_message,
            "error_id": self.exception_id,
            "severity": self.severity,
            "recovery_suggestion": self.recovery_suggestion
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization"""
        return {
            "exception_type": self.__class__.__name__,
            "message": self.message,
            "severity": self.severity,
            "category": self.category,
            "timestamp": self.timestamp,
            "exception_id": self.exception_id,
            "context": self.context,
            "recovery_suggestion": self.recovery_suggestion,
            "user_message": self.user_message,
            "technical_details": self.technical_details
        }

class ScrapingException(BaseEcoTrackerException):
    """Errors related to web scraping operations"""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        strategy: Optional[str] = None,
        http_status: Optional[int] = None,
        **kwargs
    ):
        # Build context from scraping-specific parameters
        context = kwargs.get("context", {})
        context.update({
            "url": url,
            "strategy": strategy,
            "http_status": http_status
        })
        
        # Determine category and recovery suggestion if not provided
        if "category" not in kwargs:
            if http_status in [403, 429]:
                kwargs["category"] = ErrorCategory.RATE_LIMIT
            elif http_status in [404, 410]:
                kwargs["category"] = ErrorCategory.NETWORK
            else:
                kwargs["category"] = ErrorCategory.NETWORK
        
        if "recovery_suggestion" not in kwargs:
            if http_status in [403, 429]:
                kwargs["recovery_suggestion"] = "Try again later or use a different scraping strategy"
            elif http_status in [404, 410]:
                kwargs["recovery_suggestion"] = "Check if the URL is valid and accessible"
            else:
                kwargs["recovery_suggestion"] = "Try using a different scraping strategy or check network connection"
        
        if "user_message" not in kwargs:
            kwargs["user_message"] = "Unable to extract product data. Please check the URL and try again."
        
        super().__init__(
            message,
            context=context,
            **kwargs
        )

class DataValidationException(BaseEcoTrackerException):
    """Errors related to data validation and quality checks"""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Any = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "field_name": field_name,
            "field_value": field_value,
            "validation_rule": validation_rule
        })
        
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            context=context,
            recovery_suggestion="Check input data format and try again",
            user_message="The provided data is invalid. Please check your input.",
            **kwargs
        )

class MLModelException(BaseEcoTrackerException):
    """Errors related to machine learning model operations"""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        feature_count: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "model_name": model_name,
            "feature_count": feature_count
        })
        
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            context=context,
            recovery_suggestion="Check model files and feature data integrity",
            user_message="Prediction service temporarily unavailable. Please try again later.",
            **kwargs
        )

class ConfigurationException(BaseEcoTrackerException):
    """Errors related to system configuration"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "config_key": config_key,
            "config_file": config_file
        })
        
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CONFIGURATION,
            context=context,
            recovery_suggestion="Check system configuration and environment variables",
            user_message="System configuration error. Please contact support.",
            **kwargs
        )

class RateLimitException(BaseEcoTrackerException):
    """Errors related to rate limiting and throttling"""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        service_name: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "retry_after": retry_after,
            "service_name": service_name
        })
        
        recovery_msg = f"Try again in {retry_after} seconds" if retry_after else "Try again later"
        
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RATE_LIMIT,
            context=context,
            recovery_suggestion=recovery_msg,
            user_message="Service temporarily busy. Please wait a moment and try again.",
            **kwargs
        )

class ErrorHandler:
    """
    Centralized error handling and monitoring system
    
    Provides consistent error handling patterns, monitoring integration,
    and recovery strategy management.
    """
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_handlers: Dict[type, Callable] = {}
        
    def register_handler(self, exception_type: type, handler: Callable):
        """Register custom handler for specific exception type"""
        self.error_handlers[exception_type] = handler
    
    def handle_exception(self, exception: BaseEcoTrackerException) -> Dict[str, Any]:
        """
        Handle exception with appropriate response and monitoring
        
        Args:
            exception: The exception to handle
            
        Returns:
            Dictionary with error response and metadata
        """
        # Update error counts for monitoring
        error_key = f"{exception.__class__.__name__}_{exception.category}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Check for custom handler
        if type(exception) in self.error_handlers:
            try:
                return self.error_handlers[type(exception)](exception)
            except Exception as handler_error:
                logger.error(f"Error handler failed: {handler_error}")
        
        # Default handling
        response = exception.get_user_response()
        
        # Add monitoring data
        response["monitoring"] = {
            "error_count": self.error_counts.get(error_key, 0),
            "requires_attention": exception.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]
        }
        
        return response
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring dashboard"""
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_errors": total_errors,
            "error_breakdown": self.error_counts.copy(),
            "top_errors": sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

# Global error handler instance
error_handler = ErrorHandler()

# Convenience functions
def handle_scraping_error(
    error: Exception,
    url: str,
    strategy: str,
    fallback_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handle scraping errors with appropriate fallback"""
    
    if isinstance(error, ScrapingException):
        scraping_error = error
    else:
        scraping_error = ScrapingException(
            str(error),
            url=url,
            strategy=strategy,
            severity=ErrorSeverity.MEDIUM
        )
    
    response = error_handler.handle_exception(scraping_error)
    
    # Add fallback result if available
    if fallback_result:
        response["fallback_data"] = fallback_result
        response["has_fallback"] = True
    
    return response

def validate_input_data(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate input data and raise appropriate exceptions"""
    
    for field in required_fields:
        if field not in data or data[field] is None:
            raise DataValidationException(
                f"Required field '{field}' is missing or null",
                field_name=field,
                field_value=data.get(field),
                validation_rule="required"
            )
    
    # Additional validation rules can be added here
    
if __name__ == "__main__":
    # Test the error handling framework
    print("🚨 Testing Error Handling Framework")
    print("=" * 50)
    
    try:
        raise ScrapingException(
            "Failed to extract data",
            url="https://example.com",
            strategy="requests",
            http_status=403
        )
    except ScrapingException as e:
        response = error_handler.handle_exception(e)
        print(f"Error Response: {json.dumps(response, indent=2)}")
        print(f"Error Context: {json.dumps(e.get_context(), indent=2)}")
    
    print(f"\nError Statistics: {json.dumps(error_handler.get_error_statistics(), indent=2)}")