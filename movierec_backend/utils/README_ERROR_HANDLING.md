# Comprehensive Utilities for Movie Recommendation API

This document describes the comprehensive utilities system implemented for the movie recommendation backend API, including error handling, external API clients, validation, logging, and monitoring.

## Overview

The utilities system provides:
- **Custom Exception Classes** for different types of errors
- **External API Client** with retry logic and robust error handling
- **Request/Response Logging** for monitoring and debugging
- **Input Validation** with detailed error messages
- **Consistent Error Response Format** across all endpoints
- **Middleware** for global error handling and request logging
- **Reusable Decorators** for common API patterns
- **Framework-wide Utilities** for cross-app functionality

## Components

### 1. Custom Exception Classes (`exceptions.py`)

```python
# Base exception class
class APIException(Exception):
    def __init__(self, message="An error occurred", status_code=500, error_code=None)

# Specific exception types
class ExternalAPIException(APIException)      # For TMDB API errors
class ValidationAPIException(APIException)    # For input validation errors
class AuthenticationAPIException(APIException) # For auth failures
class RateLimitAPIException(APIException)     # For rate limiting
```

### 2. Enhanced TMDB Client (`tmdb_client.py`)

Features:
- **Retry Logic**: Automatic retries with exponential backoff
- **Timeout Handling**: Configurable request timeouts
- **Status Code Handling**: Specific handling for different HTTP status codes
- **Connection Error Handling**: Robust handling of network issues
- **Session Management**: Efficient connection reuse

```python
# Example usage
client = TMDbClient()
try:
    movies = client.get_trending_movies('day')
except ExternalAPIException as e:
    # Handle external API errors
    logger.error(f"TMDB API error: {e}")
```

### 3. Decorators (`decorators.py`)

#### `@handle_api_errors`
Wraps API functions to catch and handle exceptions consistently.

#### `@validate_required_params(['param1', 'param2'])`
Validates that required query parameters are present.

#### `@validate_request_data(required_fields=['field1'], optional_fields={'field2': 'int'})`
Validates request data for POST/PUT requests.

#### `@log_api_call`
Logs API calls with timing information.

#### `@rate_limit(max_requests=100, window_seconds=60)`
Basic rate limiting (placeholder for production implementation).

#### `@cache_response(timeout=300)`
Response caching (placeholder for production implementation).

### 4. Middleware (`middleware.py`)

#### `RequestLoggingMiddleware`
- Logs all API requests and responses
- Tracks request duration
- Captures user and IP information
- Logs exceptions with context

#### `ErrorHandlingMiddleware`
- Catches unhandled exceptions
- Provides consistent error responses
- Logs unexpected errors

### 5. Example API Views (`views.py`)

Complete API endpoints demonstrating:
- Input validation
- Error handling
- Consistent response format
- Logging

## Error Response Format

All error responses follow this consistent format:

```json
{
    "success": false,
    "error": {
        "message": "Human-readable error message",
        "code": "ERROR_CODE",
        "status_code": 400,
        "details": "Additional error details (optional)"
    }
}
```

## Configuration

### Error Handling Settings

Add to your Django settings:

```python
# Error handling configuration
ERROR_HANDLING_CONFIG = {
    'ENABLE_LOGGING': True,
    'LOG_LEVEL': 'INFO',
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 1,
    'TIMEOUT': 10,
    'ENABLE_RATE_LIMITING': True,
    'RATE_LIMIT_REQUESTS': 100,
    'RATE_LIMIT_WINDOW': 60,
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/api_errors.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'utils': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# DRF exception handler
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
}

# Middleware
MIDDLEWARE = [
    # ... other middleware
    'utils.middleware.RequestLoggingMiddleware',
    'utils.middleware.ErrorHandlingMiddleware',
]
```

## Usage Examples

### 1. Basic API View with Error Handling

```python
from utils.decorators import handle_api_errors, log_api_call
from utils.exceptions import ValidationAPIException

@api_view(['GET'])
@handle_api_errors
@log_api_call
def my_api_view(request):
    try:
        # Your API logic here
        return Response({'success': True, 'data': result})
    except ValidationAPIException as e:
        return Response({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'VALIDATION_ERROR',
                'status_code': 400
            }
        }, status=400)
```

### 2. Using the TMDB Client

```python
from utils.tmdb_client import TMDbClient
from utils.exceptions import ExternalAPIException

def get_movie_data(movie_id):
    client = TMDbClient()
    try:
        movie = client.get_movie_details(movie_id)
        return movie
    except ExternalAPIException as e:
        logger.error(f"Failed to get movie {movie_id}: {e}")
        raise
```

### 3. Custom Exception Handling

```python
from utils.exceptions import APIException

class CustomAPIException(APIException):
    def __init__(self, message="Custom error", status_code=400):
        super().__init__(message, status_code, "CUSTOM_ERROR")

# Usage
raise CustomAPIException("Something went wrong", 400)
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Input validation failed | 400 |
| `AUTHENTICATION_ERROR` | Authentication failed | 401 |
| `PERMISSION_DENIED` | Access denied | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMIT_ERROR` | Rate limit exceeded | 429 |
| `EXTERNAL_API_ERROR` | External API error | 502 |
| `INTERNAL_ERROR` | Internal server error | 500 |

## Monitoring and Logging

### Log Files
- `logs/api_errors.log`: All API-related logs
- `logs/errors.log`: Error-level logs only

### Log Format
```json
{
    "timestamp": "2024-01-01 12:00:00",
    "level": "ERROR",
    "message": "API call failed",
    "function": "get_movie_details",
    "method": "GET",
    "path": "/api/movies/123/",
    "user": "user@example.com",
    "ip": "192.168.1.1",
    "duration": 1.234
}
```

## Best Practices

1. **Always use decorators** for consistent error handling
2. **Log errors with context** for debugging
3. **Validate inputs** before processing
4. **Use specific exception types** for different error scenarios
5. **Provide meaningful error messages** to clients
6. **Monitor error rates** and response times
7. **Test error scenarios** thoroughly

## Testing Error Handling

```python
import pytest
from utils.exceptions import ValidationAPIException, ExternalAPIException

def test_validation_error():
    with pytest.raises(ValidationAPIException):
        raise ValidationAPIException("Invalid input")

def test_external_api_error():
    with pytest.raises(ExternalAPIException):
        raise ExternalAPIException("TMDB API error", 502)
```

## Production Considerations

1. **Rate Limiting**: Implement proper rate limiting with Redis
2. **Caching**: Add response caching for frequently accessed data
3. **Monitoring**: Integrate with monitoring tools (Sentry, DataDog, etc.)
4. **Alerting**: Set up alerts for high error rates
5. **Circuit Breaker**: Implement circuit breaker pattern for external APIs
6. **Health Checks**: Add health check endpoints
7. **Documentation**: Keep API documentation updated with error responses

## Troubleshooting

### Common Issues

1. **TMDB API Key Not Configured**
   - Ensure `TMDB_API_KEY` is set in Django settings
   - Check environment variables

2. **High Error Rates**
   - Check external API status
   - Verify network connectivity
   - Review rate limiting settings

3. **Slow Response Times**
   - Check external API performance
   - Review timeout settings
   - Consider implementing caching

4. **Log File Issues**
   - Ensure logs directory exists
   - Check file permissions
   - Verify logging configuration

For more information, see the individual module documentation and the main project README. 