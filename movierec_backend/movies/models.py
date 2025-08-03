"""
Movie Models - Domain-specific data models for movie-related functionality.

This module defines the data models for the movies app. Currently, the app
primarily serves as an API layer that fetches data from external sources (TMDB),
but models can be added here for:

- Caching movie data locally
- User movie preferences and ratings
- Watchlist functionality
- Movie recommendations storage
- Analytics and usage tracking

All models should follow Django best practices and integrate with the
comprehensive utilities framework from the utils app for consistent
error handling, validation, and logging.
"""

from django.db import models

# Create your models here.
# Example models that could be added:

# class Movie(models.Model):
#     """Local cache of movie data from TMDB"""
#     tmdb_id = models.IntegerField(unique=True)
#     title = models.CharField(max_length=255)
#     overview = models.TextField()
#     poster_path = models.CharField(max_length=255, null=True, blank=True)
#     release_date = models.DateField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     
#     class Meta:
#         db_table = 'movies'
#         indexes = [
#             models.Index(fields=['tmdb_id']),
#             models.Index(fields=['title']),
#         ]
#     
#     def __str__(self):
#         return self.title

# class UserMoviePreference(models.Model):
#     """User preferences and ratings for movies"""
#     user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
#     is_watched = models.BooleanField(default=False)
#     is_watchlist = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     
#     class Meta:
#         db_table = 'user_movie_preferences'
#         unique_together = ['user', 'movie']
#         indexes = [
#             models.Index(fields=['user', 'rating']),
#             models.Index(fields=['user', 'is_watched']),
#             models.Index(fields=['user', 'is_watchlist']),
#         ]
#     
#     def __str__(self):
#         return f"{self.user.username} - {self.movie.title}"
