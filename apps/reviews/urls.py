"""
URL patterns for reviews app (web views).
"""
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<uuid:contract_pk>/', views.ReviewCreateView.as_view(), name='create'),
    path('user/<uuid:user_pk>/', views.UserReviewsView.as_view(), name='user_reviews'),
    path('contract/<uuid:contract_pk>/', views.ContractReviewsView.as_view(), name='contract_reviews'),
]
