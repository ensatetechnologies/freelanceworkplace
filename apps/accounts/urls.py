"""
URL patterns for accounts app (web views).
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/setup/', views.ProfileSetupView.as_view(), name='profile_setup'),
    path('profile/<uuid:pk>/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('freelancers/', views.FreelancerListView.as_view(), name='freelancer_list'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]
