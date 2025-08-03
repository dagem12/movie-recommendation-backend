"""
Movie API URL Configuration - Domain-specific movie endpoints.

This module defines the URL patterns for movie-related API endpoints.
All endpoints leverage the comprehensive utilities framework from the utils app
for consistent error handling, validation, logging, and monitoring.

URL Structure:
- /api/movies/trending/ - Get trending movies
- /api/movies/search/ - Search movies by query
- /api/movies/popular/ - Get popular movies
- /api/movies/<id>/ - Get movie details
- /api/movies/<id>/recommendations/ - Get movie recommendations

All endpoints include:
- Comprehensive error handling
- Input validation
- Request/response logging
- Performance monitoring
"""

from django.urls import path
from .views import (
    TrendingMoviesView,
    MovieSearchView,
    MovieDetailView,
    MovieRecommendationsView,
    PopularMoviesView
)

app_name = 'movies'

urlpatterns = [
    # Movie API endpoints with comprehensive error handling and validation
    path('trending/', TrendingMoviesView.as_view(), name='trending_movies'),
    path('search/', MovieSearchView.as_view(), name='search_movies'),
    path('popular/', PopularMoviesView.as_view(), name='popular_movies'),
    path('<int:movie_id>/', MovieDetailView.as_view(), name='movie_details'),
    path('<int:movie_id>/recommendations/', MovieRecommendationsView.as_view(), name='movie_recommendations'),
]