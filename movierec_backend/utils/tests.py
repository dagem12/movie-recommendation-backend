import pytest
from django.test import TestCase, RequestFactory
from django.http import Http404
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from .exceptions import (
    APIException,
    ExternalAPIException,
    ValidationAPIException,
    AuthenticationAPIException,
    RateLimitAPIException,
    custom_exception_handler
)
from .tmdb_client import TMDbClient
from .views import get_trending_movies, search_movies, get_movie_details
from .decorators import handle_api_errors, validate_required_params


class ExceptionTestCase(TestCase):
    """Test custom exception classes"""
    
    def test_api_exception(self):
        """Test base API exception"""
        exc = APIException("Test error", 400, "TEST_ERROR")
        self.assertEqual(exc.message, "Test error")
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.error_code, "TEST_ERROR")
    
    def test_external_api_exception(self):
        """Test external API exception"""
        exc = ExternalAPIException("TMDB error", 502)
        self.assertEqual(exc.message, "TMDB error")
        self.assertEqual(exc.status_code, 502)
        self.assertEqual(exc.error_code, "EXTERNAL_API_ERROR")
    
    def test_validation_exception(self):
        """Test validation exception"""
        exc = ValidationAPIException("Invalid input")
        self.assertEqual(exc.message, "Invalid input")
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.error_code, "VALIDATION_ERROR")
    
    def test_authentication_exception(self):
        """Test authentication exception"""
        exc = AuthenticationAPIException("Auth failed")
        self.assertEqual(exc.message, "Auth failed")
        self.assertEqual(exc.status_code, 401)
        self.assertEqual(exc.error_code, "AUTHENTICATION_ERROR")
    
    def test_rate_limit_exception(self):
        """Test rate limit exception"""
        exc = RateLimitAPIException("Rate limit exceeded")
        self.assertEqual(exc.message, "Rate limit exceeded")
        self.assertEqual(exc.status_code, 429)
        self.assertEqual(exc.error_code, "RATE_LIMIT_ERROR")


class ExceptionHandlerTestCase(TestCase):
    """Test custom exception handler"""
    
    def test_custom_exception_handler(self):
        """Test handling of custom exceptions"""
        exc = ValidationAPIException("Test validation error")
        context = {'view': None}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'VALIDATION_ERROR')
    
    def test_django_exception_handler(self):
        """Test handling of Django exceptions"""
        exc = Http404("Not found")
        context = {'view': None}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'NOT_FOUND')


class TMDBClientTestCase(TestCase):
    """Test TMDB client error handling"""
    
    @patch('utils.tmdb_client.requests.Session')
    def test_tmdb_client_authentication_error(self, mock_session):
        """Test TMDB client authentication error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'status_message': 'Invalid API key'}
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        with patch('utils.tmdb_client.settings') as mock_settings:
            mock_settings.TMDB_API_KEY = 'test_key'
            
            client = TMDbClient()
            
            with self.assertRaises(AuthenticationAPIException):
                client.get_trending_movies()
    
    @patch('utils.tmdb_client.requests.Session')
    def test_tmdb_client_rate_limit_error(self, mock_session):
        """Test TMDB client rate limit error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {'status_message': 'Rate limit exceeded'}
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        with patch('utils.tmdb_client.settings') as mock_settings:
            mock_settings.TMDB_API_KEY = 'test_key'
            
            client = TMDbClient()
            
            with self.assertRaises(RateLimitAPIException):
                client.get_trending_movies()
    
    @patch('utils.tmdb_client.requests.Session')
    def test_tmdb_client_timeout_error(self, mock_session):
        """Test TMDB client timeout error handling"""
        from requests.exceptions import Timeout
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = Timeout("Request timeout")
        mock_session.return_value = mock_session_instance
        
        with patch('utils.tmdb_client.settings') as mock_settings:
            mock_settings.TMDB_API_KEY = 'test_key'
            
            client = TMDbClient()
            
            with self.assertRaises(ExternalAPIException):
                client.get_trending_movies()
    
    def test_tmdb_client_validation(self):
        """Test TMDB client input validation"""
        with patch('utils.tmdb_client.settings') as mock_settings:
            mock_settings.TMDB_API_KEY = 'test_key'
            
            client = TMDbClient()
            
            # Test invalid time_window
            with self.assertRaises(ValueError):
                client.get_trending_movies('invalid')
            
            # Test invalid movie_id
            with self.assertRaises(ValueError):
                client.get_movie_details('invalid_id')
            
            # Test empty query
            with self.assertRaises(ValueError):
                client.search_movies('')


class DecoratorTestCase(TestCase):
    """Test error handling decorators"""
    
    def test_handle_api_errors_decorator(self):
        """Test handle_api_errors decorator"""
        @handle_api_errors
        def test_function():
            raise ValueError("Test error")
        
        with self.assertRaises(ValidationAPIException):
            test_function()
    
    def test_validate_required_params_decorator(self):
        """Test validate_required_params decorator"""
        @validate_required_params(['param1', 'param2'])
        def test_view(request):
            return "success"
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        with self.assertRaises(ValidationAPIException):
            test_view(request)
        
        # Test with required params
        request = factory.get('/test/?param1=value1&param2=value2')
        result = test_view(request)
        self.assertEqual(result, "success")


class APIViewTestCase(APITestCase):
    """Test API views with error handling"""
    
    @patch('utils.views.TMDbClient')
    def test_get_trending_movies_success(self, mock_client_class):
        """Test successful trending movies request"""
        mock_client = MagicMock()
        mock_client.get_trending_movies.return_value = {'results': []}
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/movies/trending/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
    
    @patch('utils.views.TMDbClient')
    def test_get_trending_movies_external_error(self, mock_client_class):
        """Test trending movies with external API error"""
        mock_client = MagicMock()
        mock_client.get_trending_movies.side_effect = ExternalAPIException("TMDB error", 502)
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/movies/trending/')
        
        self.assertEqual(response.status_code, 502)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'EXTERNAL_API_ERROR')
    
    def test_search_movies_missing_query(self):
        """Test search movies with missing query parameter"""
        response = self.client.get('/api/movies/search/')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'VALIDATION_ERROR')
    
    def test_get_movie_details_invalid_id(self):
        """Test movie details with invalid movie ID"""
        response = self.client.get('/api/movies/invalid_id/')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['code'], 'VALIDATION_ERROR')


class MiddlewareTestCase(TestCase):
    """Test middleware error handling"""
    
    def test_request_logging_middleware(self):
        """Test request logging middleware"""
        from .middleware import RequestLoggingMiddleware
        
        middleware = RequestLoggingMiddleware()
        factory = RequestFactory()
        request = factory.get('/api/test/')
        
        # Test process_request
        response = middleware.process_request(request)
        self.assertIsNone(response)
        
        # Test process_response
        from django.http import HttpResponse
        response = HttpResponse()
        result = middleware.process_response(request, response)
        self.assertEqual(result, response)
    
    def test_error_handling_middleware(self):
        """Test error handling middleware"""
        from .middleware import ErrorHandlingMiddleware
        
        middleware = ErrorHandlingMiddleware()
        factory = RequestFactory()
        request = factory.get('/api/test/')
        
        # Test with custom exception
        exc = ValidationAPIException("Test error")
        response = middleware.process_exception(request, exc)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)


if __name__ == '__main__':
    pytest.main([__file__])
