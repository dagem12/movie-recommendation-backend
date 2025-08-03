from django.urls import path
from . import views

app_name = 'utils'

urlpatterns = [
    # Movie API endpoints with error handling
    path('api/movies/trending/', views.get_trending_movies, name='trending_movies'),
    path('api/movies/search/', views.search_movies, name='search_movies'),
    path('api/movies/popular/', views.get_popular_movies, name='popular_movies'),
    path('api/movies/<int:movie_id>/', views.get_movie_details, name='movie_details'),
    path('api/movies/<int:movie_id>/recommendations/', views.get_movie_recommendations, name='movie_recommendations'),
] 