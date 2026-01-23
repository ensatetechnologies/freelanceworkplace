"""
Context processors for the application.
"""
from django.conf import settings


def site_settings(request):
    """
    Add site-wide settings to template context.
    """
    return {
        'PLATFORM_NAME': settings.PLATFORM_NAME,
        'SITE_URL': settings.SITE_URL,
        'DEBUG': settings.DEBUG,
    }
