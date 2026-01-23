"""
URL patterns for messaging app (web views).
"""
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.ConversationListView.as_view(), name='inbox'),
    path('start/', views.StartConversationView.as_view(), name='start'),
    path('<uuid:pk>/', views.ConversationDetailView.as_view(), name='conversation'),
    path('<uuid:conversation_pk>/send/', views.SendMessageView.as_view(), name='send'),
    path('<uuid:conversation_pk>/fetch/', views.FetchMessagesView.as_view(), name='fetch'),
    path('unread-count/', views.UnreadCountView.as_view(), name='unread_count'),
]
