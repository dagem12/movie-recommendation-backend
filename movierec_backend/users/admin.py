from django.contrib import admin
from .models import FavoriteMovie

@admin.register(FavoriteMovie)
class FavoriteMovieAdmin(admin.ModelAdmin):
    """
    Admin interface for FavoriteMovie model.
    
    Provides a clean interface for managing user favorite movies.
    """
    list_display = ['user', 'title', 'tmdb_id', 'release_date', 'created_at']
    list_filter = ['created_at', 'release_date', 'user']
    search_fields = ['title', 'user__username', 'tmdb_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Movie Information', {
            'fields': ('tmdb_id', 'title', 'poster_path', 'overview', 'release_date')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
