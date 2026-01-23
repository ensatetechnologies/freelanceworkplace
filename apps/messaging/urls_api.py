"""
API URL patterns for messaging app.
"""
from django.urls import path
from . import api_views

app_name = 'messaging_api'

urlpatterns = [
    path('conversations/', api_views.ConversationListView.as_view(), name='conversations'),
    path('conversations/start/', api_views.StartConversationView.as_view(), name='start'),
    path('conversations/<uuid:pk>/', api_views.ConversationDetailView.as_view(), name='conversation'),
    path('conversations/<uuid:conversation_pk>/send/', api_views.SendMessageView.as_view(), name='send'),
    path('conversations/<uuid:conversation_pk>/messages/', api_views.FetchMessagesView.as_view(), name='fetch'),
    path('<uuid:pk>/read/', api_views.MarkReadView.as_view(), name='mark_read'),
]
