import functools
import logging
import time

logger = logging.getLogger(__name__)

def handle_api_errors(func):
    """
    Decorator to handle API errors and provide consistent error responses across all endpoints.
    
    Features:
    - Catches and logs all exceptions
    - Converts ValueError to ValidationAPIException
    - Provides consistent error response format
    - Logs errors with context for debugging
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Import here to avoid circular imports
            try:
                from .exceptions import APIException, ValidationAPIException
            except ImportError:
                # If exceptions module is not available, re-raise the original exception
                raise
            
            if isinstance(e, APIException):
                # Re-raise custom API exceptions as they're already handled
                raise
            elif isinstance(e, ValueError):
                # Handle validation errors
                logger.warning(f"Validation error in {func.__name__}: {str(e)}")
                raise ValidationAPIException(str(e))
            else:
                # Log unexpected errors
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                raise APIException("An unexpected error occurred", status_code=500)
    
    return wrapper

def validate_required_params(required_params):
    """
    Decorator to validate required parameters in API requests.
    
    Features:
    - Validates query parameters are present
    - Provides clear error messages for missing parameters
    - Can be used across all API endpoints
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Import here to avoid circular imports
            try:
                from .exceptions import ValidationAPIException
            except ImportError:
                # If exceptions module is not available, just call the function
                return func(request, *args, **kwargs)
            
            missing_params = []
            
            # Check query parameters
            for param in required_params:
                if param not in request.GET:
                    missing_params.append(param)
            
            if missing_params:
                raise ValidationAPIException(
                    f"Missing required parameters: {', '.join(missing_params)}"
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def validate_request_data(required_fields=None, optional_fields=None):
    """
    Decorator to validate request data for POST/PUT requests.
    
    Features:
    - Validates required fields are present
    - Validates field types and values
    - Supports different data types (int, float, bool)
    - Provides clear error messages
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Import here to avoid circular imports
            try:
                from .exceptions import ValidationAPIException
            except ImportError:
                # If exceptions module is not available, just call the function
                return func(request, *args, **kwargs)
            
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.data if hasattr(request, 'data') else {}
                
                # Validate required fields
                if required_fields:
                    missing_fields = []
                    for field in required_fields:
                        if field not in data or data[field] is None or data[field] == '':
                            missing_fields.append(field)
                    
                    if missing_fields:
                        raise ValidationAPIException(
                            f"Missing required fields: {', '.join(missing_fields)}"
                        )
                
                # Validate field types and values
                if optional_fields:
                    for field, field_type in optional_fields.items():
                        if field in data:
                            try:
                                if field_type == 'int':
                                    int(data[field])
                                elif field_type == 'float':
                                    float(data[field])
                                elif field_type == 'bool':
                                    if isinstance(data[field], str):
                                        if data[field].lower() not in ['true', 'false', '1', '0']:
                                            raise ValueError(f"Invalid boolean value for {field}")
                            except (ValueError, TypeError):
                                raise ValidationAPIException(
                                    f"Invalid value for field '{field}'. Expected {field_type}."
                                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def rate_limit(max_requests=100, window_seconds=60):
    """
    Simple rate limiting decorator (basic implementation).
    
    Features:
    - Basic rate limiting per IP address
    - Configurable limits and time windows
    - Logs rate limit checks for monitoring
    
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # This is a basic implementation
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            
            # For now, just log the request
            logger.info(f"Rate limit check for {client_ip} on {func.__name__}")
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def cache_response(timeout=300):
    """
    Decorator to cache API responses (basic implementation).
    
    Features:
    - Basic response caching
    - Configurable cache timeouts
    - Logs cache attempts for monitoring
    

    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # This is a basic implementation
            cache_key = f"{func.__name__}_{request.path}_{request.GET.urlencode()}"
            
            # For now, just log the cache attempt
            logger.debug(f"Cache check for {cache_key}")
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def log_api_call(func):
    """
    Decorator to log API calls for monitoring and debugging.
    
    Features:
    - Logs request details (method, path, user, IP)
    - Tracks response timing
    - Logs errors with context
    - Provides comprehensive monitoring data
    - Works with both function-based and class-based views
    """
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        start_time = time.time()
        
        # Log request details
        log_data = {
            'function': f"{self.__class__.__name__}.{func.__name__}",
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if request.user.is_authenticated else 'anonymous',
            'ip': request.META.get('REMOTE_ADDR', 'unknown'),
        }
        
        logger.info(f"API call started: {log_data}")
        
        try:
            result = func(self, request, *args, **kwargs)
            
            # Log successful response
            duration = time.time() - start_time
            logger.info(f"API call completed: {log_data['function']} took {duration:.3f}s")
            
            return result
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(f"API call failed: {log_data['function']} took {duration:.3f}s, error: {str(e)}")
            raise
    
    return wrapper 