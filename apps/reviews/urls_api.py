"""
API URL patterns for reviews app.
"""
from django.urls import path
from . import api_views

app_name = 'reviews_api'

urlpatterns = [
    path('', api_views.ReviewCreateView.as_view(), name='create'),
    path('user/<uuid:user_pk>/', api_views.UserReviewsView.as_view(), name='user_reviews'),
    path('contract/<uuid:contract_pk>/', api_views.ContractReviewsView.as_view(), name='contract_reviews'),
]
