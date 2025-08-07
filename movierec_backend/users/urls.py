from django.urls import path
from .views import (
    RegisterView, 
    LoginView,
    RefreshTokenView,
    FavoriteMovieListView, 
    AddFavoriteMovieView, 
    RemoveFavoriteMovieView, 
    CheckFavoriteMovieView
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    
    # User registration
    path('register/', RegisterView.as_view(), name='register'),
    
    # Favorite movies endpoints
    path('favorites/', FavoriteMovieListView.as_view(), name='favorite-list'),
    path('favorites/add/', AddFavoriteMovieView.as_view(), name='favorite-add'),
    path('favorites/<int:pk>/remove/', RemoveFavoriteMovieView.as_view(), name='favorite-remove'),
    path('favorites/check/<int:tmdb_id>/', CheckFavoriteMovieView.as_view(), name='favorite-check'),
]