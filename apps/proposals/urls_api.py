"""
API URL patterns for proposals app.
"""
from django.urls import path
from . import api_views

app_name = 'proposals_api'

urlpatterns = [
    path('', api_views.ProposalListCreateView.as_view(), name='list_create'),
    path('my-proposals/', api_views.MyProposalsView.as_view(), name='my_proposals'),
    path('project/<uuid:project_id>/', api_views.ProjectProposalsView.as_view(), name='project_proposals'),
    path('<uuid:pk>/', api_views.ProposalDetailView.as_view(), name='detail'),
    path('<uuid:pk>/accept/', api_views.ProposalAcceptView.as_view(), name='accept'),
    path('<uuid:pk>/reject/', api_views.ProposalRejectView.as_view(), name='reject'),
    path('<uuid:pk>/shortlist/', api_views.ProposalShortlistView.as_view(), name='shortlist'),
    path('<uuid:pk>/withdraw/', api_views.ProposalWithdrawView.as_view(), name='withdraw'),
]
