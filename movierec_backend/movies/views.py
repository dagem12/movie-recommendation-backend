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
from utils.pagination import TMDbPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class TrendingMoviesView(APIView):
    """
    Get trending movies from TMDB API with pagination support
    
    Features:
    - Fetches trending movies for specified time window (day/week)
    - Supports pagination with page parameter
    - Validates time_window and page parameters
    - Handles TMDB API errors gracefully
    - Provides consistent error responses
    - Logs all requests and errors for monitoring
    """
    
    pagination_class = TMDbPagination
    
    @swagger_auto_schema(
        operation_description="""
        Get trending movies from TMDB API with pagination support.
        
        This endpoint fetches the most trending movies from TMDB API based on the specified time window.
        The results are paginated and can be cached for better performance.
        
        **Features:**
        - Fetches trending movies for day or week time window
        - Supports pagination with customizable page numbers
        - Smart pagination-aware caching for all pages
        - Comprehensive error handling and validation
        - Real-time data from TMDB API
        
        **Use Cases:**
        - Display trending movies on homepage
        - Show what's popular right now
        - Build movie discovery features
        """,
        manual_parameters=[
            openapi.Parameter(
                'time_window',
                openapi.IN_QUERY,
                description="Time window for trending movies. Use 'day' for daily trending or 'week' for weekly trending movies.",
                type=openapi.TYPE_STRING,
                enum=['day', 'week'],
                default='day'
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination. Each page contains up to 20 movies. Use this to navigate through large result sets.",
                type=openapi.TYPE_INTEGER,
                default=1,
                minimum=1
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved trending movies",
                examples={
                    "application/json": {
                        "success": True,
                        "data": [
                            {
                                "id": 123,
                                "title": "Movie Title",
                                "overview": "Movie description...",
                                "poster_path": "/path/to/poster.jpg"
                            }
                        ],
                        "pagination": {
                            "count": 10000,
                            "next": "http://localhost:8000/api/movies/trending/?page=3&time_window=day",
                            "previous": "http://localhost:8000/api/movies/trending/?page=1&time_window=day",
                            "current_page": 2,
                            "total_pages": 500,
                            "page_size": 20
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "time_window must be 'day' or 'week'",
                            "code": "VALIDATION_ERROR",
                            "status_code": 400
                        }
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "An unexpected error occurred",
                            "code": "INTERNAL_ERROR",
                            "status_code": 500
                        }
                    }
                }
            )
        },
        tags=['Movies']
    )
    @handle_api_errors
    @log_api_call
    def get(self, request):
        try:
            time_window = request.GET.get('time_window', 'day')
            if time_window not in ['day', 'week']:
                raise ValidationAPIException("time_window must be 'day' or 'week'")
            
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValidationAPIException("Page must be greater than 0")
            
            # Try to get from cache first
            cached_movies = cache_service.get_trending_movies(time_window, page)
            if cached_movies:
                paginator = self.pagination_class()
                return paginator.get_paginated_response(cached_movies)
            
            # If not in cache, fetch from API
            client = TMDbClient()
            movies = client.get_trending_movies(time_window, page)
            
            # Cache the result for this specific page
            cache_service.set_trending_movies(movies, time_window, page)
            
            # Use pagination class to format response
            paginator = self.pagination_class()
            return paginator.get_paginated_response(movies)
            
        except ValueError as e:
            logger.warning(f"Validation error in TrendingMoviesView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
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
    
    pagination_class = TMDbPagination
    
    @swagger_auto_schema(
        operation_description="""
        Search movies by query string with pagination support.
        
        This endpoint allows you to search for movies using a text query. The search is performed against
        TMDB's comprehensive movie database and returns relevant results with pagination support.
        
        **Features:**
        - Full-text search across movie titles, descriptions, and metadata
        - Paginated results for large search result sets
        - Real-time search results from TMDB API
        - Comprehensive error handling and validation
        - Support for various search terms and movie titles
        
        **Use Cases:**
        - Movie search functionality in applications
        - Finding specific movies by title or keywords
        - Building movie recommendation search features
        - Discovering movies based on user input
        
        **Search Tips:**
        - Use movie titles, actor names, or keywords
        - Search is case-insensitive
        - Partial matches are supported
        - Results are ranked by relevance
        """,
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Search query for movies. Enter movie title, actor name, or any relevant keywords. This parameter is required and cannot be empty.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination. Each page contains up to 20 search results. Use this to navigate through large search result sets.",
                type=openapi.TYPE_INTEGER,
                default=1,
                minimum=1
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved search results",
                examples={
                    "application/json": {
                        "success": True,
                        "data": [
                            {
                                "id": 123,
                                "title": "Movie Title",
                                "overview": "Movie description...",
                                "poster_path": "/path/to/poster.jpg"
                            }
                        ],
                        "pagination": {
                            "count": 1000,
                            "next": "http://localhost:8000/api/movies/search/?query=batman&page=3",
                            "previous": "http://localhost:8000/api/movies/search/?query=batman&page=1",
                            "current_page": 2,
                            "total_pages": 50,
                            "page_size": 20
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "Query parameter cannot be empty",
                            "code": "VALIDATION_ERROR",
                            "status_code": 400
                        }
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "An unexpected error occurred",
                            "code": "INTERNAL_ERROR",
                            "status_code": 500
                        }
                    }
                }
            )
        },
        tags=['Movies']
    )
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
            results = client.search_movies(query, page)
            
            # Use pagination class to format response
            paginator = self.pagination_class()
            return paginator.get_paginated_response(results)
            
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
    
    @swagger_auto_schema(
        operation_description="Get detailed movie information by TMDB movie ID",
        manual_parameters=[
            openapi.Parameter(
                'movie_id',
                openapi.IN_PATH,
                description="TMDB movie ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved movie details",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 123,
                            "title": "Movie Title",
                            "overview": "Detailed movie description...",
                            "poster_path": "/path/to/poster.jpg",
                            "release_date": "2024-01-01",
                            "vote_average": 8.5,
                            "genres": [
                                {"id": 28, "name": "Action"},
                                {"id": 12, "name": "Adventure"}
                            ]
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "Movie ID must be a valid integer",
                            "code": "VALIDATION_ERROR",
                            "status_code": 400
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="Movie not found",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "Movie not found",
                            "code": "MOVIE_NOT_FOUND",
                            "status_code": 404
                        }
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "An unexpected error occurred",
                            "code": "INTERNAL_ERROR",
                            "status_code": 500
                        }
                    }
                }
            )
        },
        tags=['Movies']
    )
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
    Get movie recommendations with pagination support
    
    Features:
    - Fetches movie recommendations based on movie ID
    - Supports pagination with page parameter
    - Validates movie_id and page parameters
    - Handles TMDB API errors gracefully
    - Provides consistent error responses
    - Logs all requests and errors for monitoring
    """
    
    pagination_class = TMDbPagination
    
    @swagger_auto_schema(
        operation_description="""
        Get movie recommendations based on movie ID with pagination support.
        
        This endpoint provides personalized movie recommendations based on a specific movie ID.
        The recommendations are generated by TMDB's sophisticated recommendation algorithm
        that analyzes movie similarities, genres, cast, and user preferences.
        
        **Features:**
        - movie recommendations based on TMDB's algorithm
        - Paginated results for browsing through recommendations
        - Smart pagination-aware caching for all pages
        - Comprehensive error handling and validation
        - Real-time recommendation data from TMDB API
        
        **Use Cases:**
        - "You might also like" movie suggestions
        - Building recommendation engines
        - Enhancing user discovery experience
        - Creating personalized movie feeds
        
        **How Recommendations Work:**
        - Based on movie similarities (genre, cast, director, etc.)
        - Considers user ratings and popularity
        - Updates dynamically as new movies are added
        - Personalized for each movie's unique characteristics
        """,
        manual_parameters=[
            openapi.Parameter(
                'movie_id',
                openapi.IN_PATH,
                description="TMDB movie ID. This is the unique identifier for the movie in TMDB's database. You can find this ID in movie detail responses or TMDB's website.",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination. Each page contains up to 20 recommended movies. Use this to explore more recommendations beyond the first page.",
                type=openapi.TYPE_INTEGER,
                default=1,
                minimum=1
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved movie recommendations",
                examples={
                    "application/json": {
                        "success": True,
                        "data": [
                            {
                                "id": 123,
                                "title": "Recommended Movie",
                                "overview": "Movie description...",
                                "poster_path": "/path/to/poster.jpg"
                            }
                        ],
                        "pagination": {
                            "count": 500,
                            "next": "http://localhost:8000/api/movies/123/recommendations/?page=3",
                            "previous": "http://localhost:8000/api/movies/123/recommendations/?page=1",
                            "current_page": 2,
                            "total_pages": 25,
                            "page_size": 20
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "Movie ID must be a valid integer",
                            "code": "VALIDATION_ERROR",
                            "status_code": 400
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="Movie not found",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "Movie not found",
                            "code": "MOVIE_NOT_FOUND",
                            "status_code": 404
                        }
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "An unexpected error occurred",
                            "code": "INTERNAL_ERROR",
                            "status_code": 500
                        }
                    }
                }
            )
        },
        tags=['Movies']
    )
    @handle_api_errors
    @log_api_call
    def get(self, request, movie_id):
        try:
            if not movie_id or not str(movie_id).isdigit():
                raise ValidationAPIException("Movie ID must be a valid integer")
            
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValidationAPIException("Page must be greater than 0")
            
            # Try to get from cache first
            cached_recommendations = cache_service.get_movie_recommendations(movie_id, page)
            if cached_recommendations:
                paginator = self.pagination_class()
                return paginator.get_paginated_response(cached_recommendations)
            
            # If not in cache, fetch from API
            client = TMDbClient()
            recommendations = client.get_movie_recommendations(movie_id, page)
            
            # Cache the result for this specific page
            cache_service.set_movie_recommendations(movie_id, recommendations, page)
            
            # Use pagination class to format response
            paginator = self.pagination_class()
            return paginator.get_paginated_response(recommendations)
            
        except ValueError as e:
            logger.warning(f"Validation error in MovieRecommendationsView: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
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
    Get popular movies with enhanced pagination support
    
    Features:
    - Fetches popular movies with pagination support
    - Validates page parameter
    - Handles TMDB API errors gracefully
    - Provides consistent error responses
    - Logs all requests and errors for monitoring
    """
    
    pagination_class = TMDbPagination
    
    @swagger_auto_schema(
        operation_description="""
        Get popular movies from TMDB API with pagination support.
        
        This endpoint fetches the most popular movies from TMDB API. Popularity is determined by
        TMDB's algorithm that considers factors like user ratings, view counts, and overall engagement.
        The list is updated regularly to reflect current trends and user preferences.
        
        **Features:**
        - Fetches currently popular movies based on TMDB's popularity algorithm
        - Paginated results for browsing through large movie collections
        - Real-time data that reflects current popularity trends
        - Comprehensive error handling and validation
        - High-quality movie data with complete metadata
        
        **Use Cases:**
        - Display popular movies on homepage or featured sections
        - Show what's trending in the movie world
        - Build movie discovery features
        - Create "Most Popular" movie lists
        
        **Popularity Factors:**
        - User ratings and reviews
        - View counts and engagement
        - Social media mentions
        - Overall cultural impact
        - Recent release status
        """,
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination. Each page contains up to 20 popular movies. Use this to explore more popular movies beyond the first page.",
                type=openapi.TYPE_INTEGER,
                default=1,
                minimum=1
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved popular movies",
                examples={
                    "application/json": {
                        "success": True,
                        "data": [
                            {
                                "id": 123,
                                "title": "Popular Movie",
                                "overview": "Movie description...",
                                "poster_path": "/path/to/poster.jpg"
                            }
                        ],
                        "pagination": {
                            "count": 20000,
                            "next": "http://localhost:8000/api/movies/popular/?page=3",
                            "previous": "http://localhost:8000/api/movies/popular/?page=1",
                            "current_page": 2,
                            "total_pages": 1000,
                            "page_size": 20
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "Page must be greater than 0",
                            "code": "VALIDATION_ERROR",
                            "status_code": 400
                        }
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": {
                            "message": "An unexpected error occurred",
                            "code": "INTERNAL_ERROR",
                            "status_code": 500
                        }
                    }
                }
            )
        },
        tags=['Movies']
    )
    @handle_api_errors
    @log_api_call
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValidationAPIException("Page must be greater than 0")
            
            client = TMDbClient()
            movies = client.get_popular_movies(page)
            
            # Use pagination class to format response
            paginator = self.pagination_class()
            return paginator.get_paginated_response(movies)
            
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
