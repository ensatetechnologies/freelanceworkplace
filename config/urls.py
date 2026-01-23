"""
URL configuration for Freelance Marketplace project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.accounts.urls_api')),
        path('projects/', include('apps.projects.urls_api')),
        path('proposals/', include('apps.proposals.urls_api')),
        path('contracts/', include('apps.contracts.urls_api')),
        path('messages/', include('apps.messaging.urls_api')),
        path('payments/', include('apps.payments.urls_api')),
        path('reviews/', include('apps.reviews.urls_api')),
        path('notifications/', include('apps.notifications.urls_api')),
    ])),
    
    # Web Views
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('projects/', include('apps.projects.urls')),
    path('proposals/', include('apps.proposals.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('messages/', include('apps.messaging.urls')),
    path('payments/', include('apps.payments.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('dashboard/', include('apps.admin_dashboard.urls')),
    
    # Django Allauth
    path('accounts/', include('allauth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
