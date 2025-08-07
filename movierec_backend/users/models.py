from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class FavoriteMovie(models.Model):
    """
    Model to store user's favorite movies.
    
    This model allows users to save movies to their favorites list.
    Movies are referenced by their TMDB ID since we're fetching from external API.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_movies')
    tmdb_id = models.IntegerField(help_text="TMDB movie ID")
    title = models.CharField(max_length=255, help_text="Movie title")
    poster_path = models.CharField(max_length=255, null=True, blank=True, help_text="Movie poster path")
    overview = models.TextField(blank=True, help_text="Movie overview/description")
    release_date = models.DateField(null=True, blank=True, help_text="Movie release date")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the movie was added to favorites")
    
    class Meta:
        db_table = 'user_favorite_movies'
        unique_together = ['user', 'tmdb_id']  # Prevent duplicate favorites
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['tmdb_id']),
        ]
        ordering = ['-created_at']  # Most recent favorites first
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
