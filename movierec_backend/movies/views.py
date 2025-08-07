"""
Movie API Views - Domain-specific movie endpoints with robust error handling.

This module contains movie-specific API endpoints that leverage the comprehensive
utilities framework from the utils app for consistent error handling, validation,
logging, and monitoring.

Features:
- Movie data retrieval from TMDB API
- Input validation and sanitization
- Comprehensive error handling with consistent responses
- Request/response logging and monitoring
- Performance tracking and debugging
- Reusable error handling patterns

All endpoints use decorators from utils.decorators for consistent behavior:
- @handle_api_errors: Catches and handles all exceptions
- @log_api_call: Logs request details and timing
- Custom exception handling for specific error scenarios
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.tmdb_client import TMDbClient
from utils.cache_service import cache_service
from utils.exceptions import ExternalAPIException, ValidationAPIException
from utils.decorators import handle_api_errors, log_api_call
import logging

logger = logging.getLogger(__name__)

class TrendingMoviesView(APIView):
    """
    Get trending movies from TMDB API
    
    Features:
    - Fetches trending movies for specified time window (day/week)
    - Validates time_window parameter
    - Handles TMDB API errors gracefully
    - Provides consistent error responses
    - Logs all requests and errors for monitoring
    """
    
    @handle_api_errors
    @log_api_call
    def get(self, request):
        try:
            time_window = request.GET.get('time_window', 'day')
            if time_window not in ['day', 'week']:
                raise ValidationAPIException("time_window must be 'day' or 'week'")
            
            # Try to get from cache first
            cached_movies = cache_service.get_trending_movies(time_window)
            if cached_movies:
                return Response({
                    'success': True,
                    'data': cached_movies,
                    'time_window': time_window,
                    'cached': True
                })
            
            # If not in cache, fetch from API
            client = TMDbClient()
            movies = client.get_trending_movies(time_window)
            
            
            # Cache the result
            cache_service.set_trending_movies(movies, time_window)
            
            return Response({
                'success': True,
                'data': movies,
                'time_window': time_window,
                'cached': False
            })
            
        except ExternalAPIException as e:
            logger.error(f"External API error in TrendingMoviesView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in TrendingMoviesView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

class MovieSearchView(APIView):
    """
    Search movies with comprehensive error handling and input validation.
    
    Features:
    - Searches movies by query string
    - Validates required query parameter
    - Supports pagination with page parameter
    - Handles TMDB API errors gracefully
    - Provides consistent error responses
    - Logs all requests and errors for monitoring
    """
    
    @handle_api_errors
    @log_api_call
    def get(self, request):
        try:
            query = request.GET.get('query', '').strip()
            if not query:
                raise ValidationAPIException("Query parameter cannot be empty")
            
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValidationAPIException("Page must be greater than 0")
            
            client = TMDbClient()
            results = client.search_movies(query)
            
            return Response({
                'success': True,
                'data': results,
                'query': query,
                'page': page
            })
            
        except ValueError as e:
            logger.warning(f"Validation error in MovieSearchView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
        except ExternalAPIException as e:
            logger.error(f"External API error in MovieSearchView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in MovieSearchView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

class MovieDetailView(APIView):
    """
    Get movie details 

    Features:
    - Fetches detailed movie information by ID
    - Validates movie_id parameter
    - Handles TMDB API errors gracefully
    - Provides consistent error responses
    - Logs all requests and errors for monitoring
    """
    
    @handle_api_errors
    @log_api_call
    def get(self, request, movie_id):
        try:
            if not movie_id or not str(movie_id).isdigit():
                raise ValidationAPIException("Movie ID must be a valid integer")
            
            client = TMDbClient()
            movie = client.get_movie_details(movie_id)
            
            return Response({
                'success': True,
                'data': movie
            })
            
        except ValidationAPIException as e:
            logger.warning(f"Validation error in MovieDetailView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
        except ExternalAPIException as e:
            logger.error(f"External API error in MovieDetailView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in MovieDetailView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

class MovieRecommendationsView(APIView):
    """
    Get movie recommendations
    
    Features:
    - Fetches movie recommendations based on movie ID
    - Validates movie_id parameter
    - Handles TMDB API errors gracefully
    - Provides consistent error responses
    - Logs all requests and errors for monitoring
    """
    
    @handle_api_errors
    @log_api_call
    def get(self, request, movie_id):
        try:
            if not movie_id or not str(movie_id).isdigit():
                raise ValidationAPIException("Movie ID must be a valid integer")
            
            # Try to get from cache first
            cached_recommendations = cache_service.get_movie_recommendations(movie_id)
            if cached_recommendations:
                return Response({
                    'success': True,
                    'data': cached_recommendations,
                    'cached': True
                })
            
            # If not in cache, fetch from API
            client = TMDbClient()
            recommendations = client.get_movie_recommendations(movie_id)
            
            # Cache the result
            cache_service.set_movie_recommendations(movie_id, recommendations)
            
            return Response({
                'success': True,
                'data': recommendations,
                'cached': False
            })
            
        except ValidationAPIException as e:
            logger.warning(f"Validation error in MovieRecommendationsView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
        except ExternalAPIException as e:
            logger.error(f"External API error in MovieRecommendationsView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in MovieRecommendationsView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

class PopularMoviesView(APIView):
    """
    Get popular movies
    
    Features:
    - Fetches popular movies with pagination support
    - Validates page parameter
    - Handles TMDB API errors gracefully
    - Provides consistent error responses
    - Logs all requests and errors for monitoring
    """
    
    @handle_api_errors
    @log_api_call
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValidationAPIException("Page must be greater than 0")
            
            client = TMDbClient()
            movies = client.get_popular_movies(page)
            
            return Response({
                'success': True,
                'data': movies,
                'page': page
            })
            
        except ValueError as e:
            logger.warning(f"Validation error in PopularMoviesView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
        except ExternalAPIException as e:
            logger.error(f"External API error in PopularMoviesView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in PopularMoviesView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)
