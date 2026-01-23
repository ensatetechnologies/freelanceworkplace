"""
API views for proposals app.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsFreelancer, IsClient, IsProposalOwner
from .models import Proposal
from .serializers import (
    ProposalListSerializer,
    ProposalDetailSerializer,
    ProposalCreateSerializer
)


class ProposalListCreateView(generics.ListCreateAPIView):
    """List and create proposals."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProposalCreateSerializer
        return ProposalListSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Freelancers see their own proposals
        if user.role == 'freelancer':
            return Proposal.objects.filter(
                freelancer=user
            ).select_related('project', 'project__client')
        
        # Clients see proposals for their projects
        return Proposal.objects.filter(
            project__client=user
        ).select_related('freelancer', 'project')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsFreelancer()]
        return [IsAuthenticated()]


class ProposalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete proposal."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProposalCreateSerializer
        return ProposalDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        from django.db.models import Q
        return Proposal.objects.filter(
            Q(freelancer=user) | Q(project__client=user)
        ).select_related('project', 'freelancer', 'project__client')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Mark as viewed if client is viewing
        if request.user == instance.project.client:
            instance.mark_viewed()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MyProposalsView(generics.ListAPIView):
    """List current user's proposals."""
    permission_classes = [IsAuthenticated, IsFreelancer]
    serializer_class = ProposalListSerializer
    
    def get_queryset(self):
        queryset = Proposal.objects.filter(
            freelancer=self.request.user
        ).select_related('project')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class ProjectProposalsView(generics.ListAPIView):
    """List proposals for a specific project."""
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = ProposalListSerializer
    
    def get_queryset(self):
        from apps.projects.models import Project
        project_id = self.kwargs.get('project_id')
        
        return Proposal.objects.filter(
            project_id=project_id,
            project__client=self.request.user
        ).select_related('freelancer')


class ProposalAcceptView(APIView):
    """Accept a proposal."""
    permission_classes = [IsAuthenticated, IsClient]
    
    def post(self, request, pk):
        proposal = Proposal.objects.filter(
            pk=pk,
            project__client=request.user,
            status__in=['pending', 'shortlisted']
        ).first()
        
        if not proposal:
            return Response(
                {'error': 'Proposal not found or cannot be accepted.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        proposal.accept()
        
        # Create contract
        from apps.contracts.models import Contract
        from django.utils import timezone
        
        contract = Contract.objects.create(
            project=proposal.project,
            proposal=proposal,
            client=proposal.project.client,
            freelancer=proposal.freelancer,
            title=proposal.project.title,
            description=proposal.project.description,
            total_amount=proposal.bid_amount,
            start_date=timezone.now().date()
        )
        
        return Response({
            'message': 'Proposal accepted. Contract created.',
            'contract_id': str(contract.id)
        })


class ProposalRejectView(APIView):
    """Reject a proposal."""
    permission_classes = [IsAuthenticated, IsClient]
    
    def post(self, request, pk):
        proposal = Proposal.objects.filter(
            pk=pk,
            project__client=request.user,
            status__in=['pending', 'shortlisted']
        ).first()
        
        if not proposal:
            return Response(
                {'error': 'Proposal not found or cannot be rejected.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        proposal.reject()
        return Response({'message': 'Proposal rejected.'})


class ProposalShortlistView(APIView):
    """Shortlist a proposal."""
    permission_classes = [IsAuthenticated, IsClient]
    
    def post(self, request, pk):
        proposal = Proposal.objects.filter(
            pk=pk,
            project__client=request.user,
            status='pending'
        ).first()
        
        if not proposal:
            return Response(
                {'error': 'Proposal not found or cannot be shortlisted.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        proposal.shortlist()
        return Response({'message': 'Proposal shortlisted.'})


class ProposalWithdrawView(APIView):
    """Withdraw a proposal."""
    permission_classes = [IsAuthenticated, IsFreelancer]
    
    def post(self, request, pk):
        proposal = Proposal.objects.filter(
            pk=pk,
            freelancer=request.user,
            status__in=['pending', 'shortlisted']
        ).first()
        
        if not proposal:
            return Response(
                {'error': 'Proposal not found or cannot be withdrawn.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        proposal.withdraw()
        return Response({'message': 'Proposal withdrawn.'})
