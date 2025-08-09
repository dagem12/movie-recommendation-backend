

from django.urls import path
from . import views

app_name = 'utils'

urlpatterns = [
    path('cache/', views.CacheManagementView.as_view(), name='cache-management'),
    
    # Settings management endpoints
    path('settings/', views.SettingsListView.as_view(), name='settings-list'),
    path('settings/<int:id>/', views.SettingsDetailView.as_view(), name='settings-detail'),
    path('settings/code/<str:setting_code>/', views.SettingsByCodeView.as_view(), name='settings-by-code'),
] 