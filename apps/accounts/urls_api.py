"""
API URL patterns for accounts app.
"""
from django.urls import path
from . import api_views

app_name = 'accounts_api'

urlpatterns = [
    path('register/', api_views.RegisterView.as_view(), name='register'),
    path('login/', api_views.LoginView.as_view(), name='login'),
    path('logout/', api_views.LogoutView.as_view(), name='logout'),
    path('user/', api_views.CurrentUserView.as_view(), name='current_user'),
    path('profile/', api_views.ProfileView.as_view(), name='profile'),
    path('profile/<uuid:pk>/', api_views.PublicProfileView.as_view(), name='public_profile'),
    path('freelancers/', api_views.FreelancerListView.as_view(), name='freelancer_list'),
]
