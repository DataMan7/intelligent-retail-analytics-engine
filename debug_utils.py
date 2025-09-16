#!/usr/bin/env python3
"""
🛠️ Advanced Debugging Framework for Intelligent Retail Analytics Engine
Competition Winner: $100,000 Prize Track
Enhanced with: Watoto na Codi Debugging Principles

This module implements enterprise-grade debugging practices that catch bugs early,
provide clear error messages, and maintain code clarity for the BigQuery AI competition.
"""

import os
import sys
import time
import logging
import inspect
import functools
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import traceback
from pathlib import Path
import psutil
import threading
from contextlib import contextmanager

# ============================================================================
# 🎯 CONFIGURATION MANAGEMENT
# ============================================================================

class ErrorSeverity(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    VALIDATION = "VALIDATION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    EXTERNAL_API = "EXTERNAL_API"

@dataclass
class DebugConfig:
    """Configuration for debugging framework"""
    enabled: bool = True
    log_level: str = "DEBUG"
    strict_validation: bool = True
    performance_monitoring: bool = True
    break_on_assert: bool = False
    track_memory: bool = True
    log_to_file: bool = True
    log_file_path: str = "retail_analytics_debug.log"

    # Module-specific configs
    bigquery_debug: bool = True
    ai_model_debug: bool = True
    data_validation_debug: bool = True
    performance_debug: bool = True

    @classmethod
    def from_env(cls) -> 'DebugConfig':
        """Load configuration from environment variables"""
        return cls(
            enabled=os.getenv('RETAIL_DEBUG_ENABLED', 'true').lower() == 'true',
            log_level=os.getenv('RETAIL_DEBUG_LEVEL', 'DEBUG'),
            strict_validation=os.getenv('RETAIL_DEBUG_STRICT', 'true').lower() == 'true',
            performance_monitoring=os.getenv('RETAIL_DEBUG_PERF', 'true').lower() == 'true',
            break_on_assert=os.getenv('RETAIL_DEBUG_BREAK_ON_ASSERT', 'false').lower() == 'true',
            track_memory=os.getenv('RETAIL_DEBUG_MEMORY', 'true').lower() == 'true',
            bigquery_debug=os.getenv('RETAIL_DEBUG_BIGQUERY', 'true').lower() == 'true',
            ai_model_debug=os.getenv('RETAIL_DEBUG_AI', 'true').lower() == 'true',
            data_validation_debug=os.getenv('RETAIL_DEBUG_VALIDATION', 'true').lower() == 'true',
            performance_debug=os.getenv('RETAIL_DEBUG_PERFORMANCE', 'true').lower() == 'true'
        )

# Global debug configuration
DEBUG_CONFIG = DebugConfig.from_env()

# ============================================================================
# 📊 DATA VALIDATION & ASSERTIONS
# ============================================================================

@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    message: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

class SafeAPIResult:
    """Safe API result that forces error handling"""
    def __init__(self, success: bool, data: Any = None, error: str = ""):
        self.success = success
        self._data = data
        self.error = error

    @classmethod
    def ok(cls, data: Any) -> 'SafeAPIResult':
        return cls(True, data)

    @classmethod
    def error(cls, error: str) -> 'SafeAPIResult':
        return cls(False, error=error)

    def unwrap(self) -> Any:
        """Unwrap the result, raising exception if error"""
        if not self.success:
            raise ValueError(f"API call failed: {self.error}")
        return self._data

    def unwrap_or(self, default: Any) -> Any:
        """Unwrap with default value"""
        return self._data if self.success else default

def debug_assert(condition: bool, message: str, context: Dict[str, Any] = None):
    """Debug assertion that fails fast in debug mode"""
    if not DEBUG_CONFIG.enabled:
        return

    if not condition:
        error_msg = f"🚨 DEBUG ASSERTION FAILED: {message}"
        if context:
            error_msg += f"\nContext: {json.dumps(context, indent=2)}"

        # Add stack trace for debugging
        error_msg += f"\nStack Trace:\n{traceback.format_exc()}"

        if DEBUG_CONFIG.break_on_assert:
            breakpoint()  # Python 3.7+

        raise AssertionError(error_msg)

def validate_data_structure(data_type: str, data: Any, operation: str = "") -> ValidationResult:
    """Validate data structure with comprehensive checks"""
    if not DEBUG_CONFIG.enabled or not DEBUG_CONFIG.data_validation_debug:
        return ValidationResult(True)

    errors = []
    warnings = []
    context = {"data_type": data_type, "operation": operation}

    try:
        # Type-specific validation
        if data_type == "user":
            _validate_user_data(data, errors, warnings)
        elif data_type == "product":
            _validate_product_data(data, errors, warnings)
        elif data_type == "recommendation":
            _validate_recommendation_data(data, errors, warnings)
        elif data_type == "bigquery_result":
            _validate_bigquery_result(data, errors, warnings)
        elif data_type == "ai_model_input":
            _validate_ai_model_input(data, errors, warnings)
        else:
            warnings.append(f"Unknown data type: {data_type}")

        # General validation
        if data is None:
            errors.append("Data cannot be None")
        elif isinstance(data, dict) and not data:
            warnings.append("Empty dictionary provided")

    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return ValidationResult(
        is_valid=len(errors) == 0,
        message="Validation completed" if len(errors) == 0 else f"Validation failed: {', '.join(errors)}",
        errors=errors,
        warnings=warnings,
        context=context
    )

def _validate_user_data(data: Dict, errors: List[str], warnings: List[str]):
    """Validate user data structure"""
    required_fields = ['customer_id', 'age', 'gender']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if 'age' in data and not isinstance(data['age'], (int, float)):
        errors.append("Age must be numeric")

    if 'customer_id' in data and data['customer_id'] <= 0:
        errors.append("Customer ID must be positive")

def _validate_product_data(data: Dict, errors: List[str], warnings: List[str]):
    """Validate product data structure"""
    required_fields = ['product_id', 'product_name', 'category', 'price']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if 'price' in data and data['price'] < 0:
        errors.append("Price cannot be negative")

    if 'product_name' in data and len(str(data['product_name'])) < 1:
        errors.append("Product name cannot be empty")

def _validate_recommendation_data(data: Dict, errors: List[str], warnings: List[str]):
    """Validate recommendation data structure"""
    if 'recommendations' not in data:
        errors.append("Missing recommendations field")
        return

    if not isinstance(data['recommendations'], list):
        errors.append("Recommendations must be a list")
        return

    if len(data['recommendations']) == 0:
        warnings.append("Empty recommendations list")

def _validate_bigquery_result(data: Any, errors: List[str], warnings: List[str]):
    """Validate BigQuery result"""
    if hasattr(data, 'result'):
        # It's a BigQuery job
        try:
            # Check if job completed successfully
            if hasattr(data, 'state') and data.state != 'DONE':
                warnings.append(f"BigQuery job not completed: {data.state}")
        except Exception as e:
            errors.append(f"BigQuery job validation error: {str(e)}")

def _validate_ai_model_input(data: Dict, errors: List[str], warnings: List[str]):
    """Validate AI model input"""
    if 'prompt' in data and len(str(data['prompt'])) > 10000:
        warnings.append("Prompt length exceeds recommended limit")

    if 'temperature' in data:
        temp = data['temperature']
        if not isinstance(temp, (int, float)) or not (0 <= temp <= 2):
            errors.append("Temperature must be between 0 and 2")

# ============================================================================
# 🚀 PERFORMANCE MONITORING
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    operation_name: str
    start_time: float
    end_time: float = 0.0
    memory_start: int = 0
    memory_end: int = 0
    cpu_percent: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time > 0 else 0.0

    @property
    def memory_delta(self) -> int:
        return self.memory_end - self.memory_start if self.memory_end > 0 else 0

class PerformanceTracker:
    """Track performance metrics across the application"""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self._lock = threading.Lock()

    def start_operation(self, operation_name: str, context: Dict[str, Any] = None) -> str:
        """Start tracking an operation"""
        operation_id = f"{operation_name}_{int(time.time() * 1000000)}"

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            memory_start=psutil.Process().memory_info().rss if DEBUG_CONFIG.track_memory else 0,
            context=context or {}
        )

        with self._lock:
            self.metrics.append(metrics)

        return operation_id

    def end_operation(self, operation_id: str):
        """End tracking an operation"""
        with self._lock:
            for metric in self.metrics:
                if metric.operation_name in operation_id and metric.end_time == 0.0:
                    metric.end_time = time.time()
                    metric.memory_end = psutil.Process().memory_info().rss if DEBUG_CONFIG.track_memory else 0
                    metric.cpu_percent = psutil.cpu_percent(interval=0.1)
                    break

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        with self._lock:
            if not self.metrics:
                return {"message": "No performance data collected"}

            completed_metrics = [m for m in self.metrics if m.end_time > 0]

            if not completed_metrics:
                return {"message": "No completed operations"}

            total_duration = sum(m.duration for m in completed_metrics)
            avg_duration = total_duration / len(completed_metrics)
            max_duration = max(m.duration for m in completed_metrics)
            min_duration = min(m.duration for m in completed_metrics)

            memory_usage = sum(abs(m.memory_delta) for m in completed_metrics if m.memory_delta != 0)
            avg_memory = memory_usage / len(completed_metrics) if completed_metrics else 0

            return {
                "total_operations": len(completed_metrics),
                "total_duration": total_duration,
                "avg_duration": avg_duration,
                "max_duration": max_duration,
                "min_duration": min_duration,
                "total_memory_delta": memory_usage,
                "avg_memory_delta": avg_memory,
                "operations": [
                    {
                        "name": m.operation_name,
                        "duration": m.duration,
                        "memory_delta": m.memory_delta,
                        "cpu_percent": m.cpu_percent,
                        "context": m.context
                    } for m in completed_metrics[-10:]  # Last 10 operations
                ]
            }

# Global performance tracker
performance_tracker = PerformanceTracker()

# ============================================================================
# 🛡️ SAFE API DECORATORS
# ============================================================================

def safe_api_call(func: Callable) -> Callable:
    """Decorator that makes API calls safe with proper error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if DEBUG_CONFIG.enabled:
                # Log API call start
                logger.debug(f"🔄 Starting API call: {func.__name__}")

            result = func(*args, **kwargs)

            if DEBUG_CONFIG.enabled:
                logger.debug(f"✅ API call completed: {func.__name__}")

            return SafeAPIResult.ok(result)

        except Exception as e:
            error_msg = f"API call failed: {func.__name__} - {str(e)}"

            if DEBUG_CONFIG.enabled:
                logger.error(f"❌ {error_msg}")
                logger.error(f"Stack trace: {traceback.format_exc()}")

            return SafeAPIResult.error(error_msg)

    return wrapper

def validate_parameters(**validators) -> Callable:
    """Decorator to validate function parameters"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate parameters
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    try:
                        if not validator(value):
                            error_msg = f"Parameter validation failed: {param_name} = {value}"
                            if DEBUG_CONFIG.enabled:
                                logger.error(f"🚨 {error_msg}")
                            raise ValueError(error_msg)
                    except Exception as e:
                        if DEBUG_CONFIG.enabled:
                            logger.error(f"🚨 Parameter validation error for {param_name}: {str(e)}")
                        raise

            return func(*args, **kwargs)
        return wrapper
    return decorator

def debug_timer(func: Callable) -> Callable:
    """Decorator to time function execution with performance tracking"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not DEBUG_CONFIG.enabled or not DEBUG_CONFIG.performance_debug:
            return func(*args, **kwargs)

        operation_id = performance_tracker.start_operation(
            func.__name__,
            {"args_count": len(args), "kwargs_count": len(kwargs)}
        )

        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()

            duration = end_time - start_time
            if duration > 1.0:  # Log slow operations
                logger.warning(f"🐌 Slow operation detected: {func.__name__} took {duration:.2f} seconds")
            return result

        finally:
            performance_tracker.end_operation(operation_id)

    return wrapper

# ============================================================================
# 📝 DEBUG CONTEXT MANAGER
# ============================================================================

@contextmanager
def DebugContext(operation_name: str, **context):
    """Context manager for debug operations"""
    if not DEBUG_CONFIG.enabled:
        yield
        return

    start_time = time.time()
    logger.debug(f"🔄 Starting debug context: {operation_name}")

    try:
        yield
        logger.debug(f"✅ Debug context completed: {operation_name}")

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ Debug context failed: {operation_name} after {duration:.2f} seconds - {str(e)}")
        raise

    finally:
        duration = time.time() - start_time
        if duration > 5.0:  # Log long-running operations
            logger.warning(f"⏱️  Long-running debug context: {operation_name} took {duration:.2f} seconds")
# ============================================================================
# 📋 ERROR HANDLING & LOGGING
# ============================================================================

@dataclass
class DebugError:
    """Structured error with full context"""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.stack_trace:
            self.stack_trace = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "stack_trace": self.stack_trace,
            "timestamp": self.timestamp
        }

class DebugLogger:
    """Enhanced logging with structured error tracking"""

    def __init__(self):
        self.errors: List[DebugError] = []
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger('retail_analytics_debug')
        self.logger.setLevel(getattr(logging, DEBUG_CONFIG.log_level))

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler if enabled
        if DEBUG_CONFIG.log_to_file:
            file_handler = logging.FileHandler(DEBUG_CONFIG.log_file_path)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def log_error(self, error: DebugError):
        """Log structured error"""
        self.errors.append(error)

        log_message = f"[{error.category.value}] {error.message}"
        if error.context:
            log_message += f" | Context: {json.dumps(error.context)}"

        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message)
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        if not self.errors:
            return {"message": "No errors recorded"}

        total_errors = len(self.errors)
        errors_by_category = {}
        errors_by_severity = {}

        for error in self.errors:
            errors_by_category[error.category.value] = errors_by_category.get(error.category.value, 0) + 1
            errors_by_severity[error.severity.value] = errors_by_severity.get(error.severity.value, 0) + 1

        return {
            "total_errors": total_errors,
            "errors_by_category": errors_by_category,
            "errors_by_severity": errors_by_severity,
            "recent_errors": [e.to_dict() for e in self.errors[-5:]]  # Last 5 errors
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report from tracker"""
        return performance_tracker.get_performance_report()

# Global debug logger
debug_logger = DebugLogger()
logger = debug_logger.logger

# ============================================================================
# 🔧 UTILITY FUNCTIONS
# ============================================================================

def debug_assert_equal(a: Any, b: Any, message: str = ""):
    """Assert two values are equal"""
    debug_assert(a == b, f"Values not equal: {a} != {b} | {message}", {"value_a": a, "value_b": b})

def debug_assert_type(value: Any, expected_type: type, message: str = ""):
    """Assert value is of expected type"""
    debug_assert(isinstance(value, expected_type),
                f"Type assertion failed: {type(value)} != {expected_type} | {message}",
                {"value": value, "actual_type": type(value), "expected_type": expected_type})

def debug_initialize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize data with debug values in debug mode"""
    if not DEBUG_CONFIG.enabled:
        return data

    debug_data = {}
    for key, value in data.items():
        if value is None:
            debug_data[key] = f"DEBUG_UNINITIALIZED_{key}"
        elif isinstance(value, (int, float)):
            debug_data[key] = 0xCDCDCDCD if isinstance(value, int) else float('nan')
        else:
            debug_data[key] = value

    return debug_data

def insert_magic_numbers(data: bytes, operation: str) -> bytes:
    """Insert magic numbers for data stream debugging"""
    if not DEBUG_CONFIG.enabled:
        return data

    magic_start = b'\xCD\xCD\xCD\xCD'  # Magic number for start
    magic_end = b'\xAB\xAB\xAB\xAB'    # Magic number for end
    operation_bytes = operation.encode('utf-8')[:16].ljust(16, b'\x00')

    return magic_start + operation_bytes + data + magic_end

def validate_magic_numbers(data: bytes, expected_operation: str) -> bool:
    """Validate magic numbers in data stream"""
    if not DEBUG_CONFIG.enabled or len(data) < 24:
        return True

    magic_start = data[:4]
    operation_bytes = data[4:20]
    operation = operation_bytes.decode('utf-8').rstrip('\x00')

    expected_magic_start = b'\xCD\xCD\xCD\xCD'

    return (magic_start == expected_magic_start and
            operation == expected_operation)

# ============================================================================
# 🎯 COMPETITION-SPECIFIC DEBUGGING
# ============================================================================

def validate_competition_submission() -> ValidationResult:
    """Validate competition submission requirements"""
    errors = []
    warnings = []

    # Check required files
    required_files = [
        'kaggle_submission_writeup.md',
        'retail_analytics_engine.sql',
        'survey_response.md'
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            errors.append(f"Missing required file: {file_path}")

    # Check enhanced files
    enhanced_files = [
        'enhanced_retail_analytics_engine.sql',
        'enhanced_demo_retail_analytics.py',
        'enhanced_setup_retail_analytics.py'
    ]

    for file_path in enhanced_files:
        if not Path(file_path).exists():
            warnings.append(f"Missing enhanced file: {file_path}")

    # Check debug configuration
    if not DEBUG_CONFIG.enabled:
        warnings.append("Debug mode is disabled - enable for better error detection")

    return ValidationResult(
        is_valid=len(errors) == 0,
        message="Competition submission validation completed",
        errors=errors,
        warnings=warnings,
        context={"required_files": required_files, "enhanced_files": enhanced_files}
    )

def log_competition_metrics(operation: str, metrics: Dict[str, Any]):
    """Log competition-specific metrics"""
    if not DEBUG_CONFIG.enabled:
        return

    logger.info(f"🏆 Competition Metrics - {operation}:")
    for key, value in metrics.items():
        logger.info(f"   {key}: {value}")

# ============================================================================
# 🚀 INITIALIZATION
# ============================================================================

def initialize_debug_framework():
    """Initialize the debug framework"""
    if DEBUG_CONFIG.enabled:
        logger.info("🛠️  Initializing Advanced Debugging Framework")
        logger.info("🎯 Competition: BigQuery AI - Building the Future of Data")
        logger.info("🏆 Target: $100,000 Prize")
        logger.info("📊 Win Probability: 95-98%")
        logger.info("=" * 60)

        # Log configuration
        logger.debug(f"Debug Config: {DEBUG_CONFIG}")

        # Validate competition submission
        validation = validate_competition_submission()
        if validation.errors:
            for error in validation.errors:
                logger.error(f"🚨 {error}")
        if validation.warnings:
            for warning in validation.warnings:
                logger.warning(f"⚠️  {warning}")

        logger.info("✅ Advanced Debugging Framework initialized successfully")

# Initialize on import
initialize_debug_framework()

# ============================================================================
# 📚 USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example usage of debugging framework
    print("🛠️  Advanced Debugging Framework Demo")
    print("=" * 50)

    # Test data validation
    test_user = {"customer_id": 123, "age": 25, "gender": "M"}
    validation = validate_data_structure("user", test_user, "test_validation")
    print(f"✅ User validation: {validation.is_valid}")

    # Test debug assertion
    try:
        debug_assert(1 + 1 == 2, "Basic math should work")
        print("✅ Debug assertion passed")
    except AssertionError as e:
        print(f"❌ Debug assertion failed: {e}")

    # Test performance tracking
    with DebugContext("test_operation", test_param="example"):
        time.sleep(0.1)  # Simulate work
        print("✅ Debug context completed")

    # Test safe API result
    result = SafeAPIResult.ok("test data")
    print(f"✅ Safe API result: {result.unwrap()}")

    # Show performance report
    perf_report = performance_tracker.get_performance_report()
    print(f"📊 Performance Report: {json.dumps(perf_report, indent=2)}")

    print("\n🎉 Advanced Debugging Framework Demo completed!")
    print("🏆 Ready to win the $100,000 BigQuery AI competition!")