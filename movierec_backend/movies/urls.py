from django.urls import path
from .views import TrendingMoviesView

urlpatterns = [
    path('trending/', TrendingMoviesView.as_view(), name='trending-movies'),
]