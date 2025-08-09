from django.contrib import admin
from .models import Settings

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for Settings model.
    
    Provides a user-friendly interface for managing system settings.
    """
    list_display = ['setting_code', 'description', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['setting_code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['setting_code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('setting_code', 'description', 'is_active')
        }),
        ('Setting Value', {
            'fields': ('setting_value',),
            'description': 'Enter valid JSON data for the setting configuration'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make setting_code readonly when editing existing settings"""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('setting_code',)
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of settings"""
        return True
    
    def save_model(self, request, obj, form, change):
        """Custom save logic for settings"""
        if not change:  # Creating new setting
            obj.setting_code = obj.setting_code.strip()
        super().save_model(request, obj, form, change)
