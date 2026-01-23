"""
API URL patterns for notifications app.
"""
from django.urls import path
from . import api_views

app_name = 'notifications_api'

urlpatterns = [
    path('', api_views.NotificationListView.as_view(), name='list'),
    path('<uuid:pk>/read/', api_views.MarkAsReadView.as_view(), name='mark_read'),
    path('read-all/', api_views.MarkAllAsReadView.as_view(), name='mark_all_read'),
    path('unread-count/', api_views.UnreadCountView.as_view(), name='unread_count'),
]
