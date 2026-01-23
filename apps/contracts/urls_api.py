"""
API URL patterns for contracts app.
"""
from django.urls import path
from . import api_views

app_name = 'contracts_api'

urlpatterns = [
    path('', api_views.ContractListView.as_view(), name='list'),
    path('<uuid:pk>/', api_views.ContractDetailView.as_view(), name='detail'),
    path('<uuid:pk>/complete/', api_views.ContractCompleteView.as_view(), name='complete'),
    path('<uuid:contract_pk>/milestones/', api_views.MilestoneCreateView.as_view(), name='milestone_create'),
    path('milestones/<uuid:pk>/<str:action>/', api_views.MilestoneActionView.as_view(), name='milestone_action'),
]
