"""
API views for contracts app.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q

from apps.core.permissions import IsContractParticipant
from .models import Contract, Milestone, ContractActivity
from .serializers import (
    ContractListSerializer,
    ContractDetailSerializer,
    MilestoneSerializer,
    MilestoneCreateSerializer
)


class ContractListView(generics.ListAPIView):
    """List user's contracts."""
    permission_classes = [IsAuthenticated]
    serializer_class = ContractListSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Contract.objects.filter(
            Q(client=user) | Q(freelancer=user)
        ).select_related('client', 'freelancer')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class ContractDetailView(generics.RetrieveAPIView):
    """Retrieve contract details."""
    permission_classes = [IsAuthenticated, IsContractParticipant]
    serializer_class = ContractDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Contract.objects.filter(
            Q(client=user) | Q(freelancer=user)
        ).select_related('client', 'freelancer').prefetch_related('milestones')


class MilestoneCreateView(APIView):
    """Create a milestone for a contract."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, contract_pk):
        contract = Contract.objects.filter(
            pk=contract_pk, client=request.user, status='active'
        ).first()
        
        if not contract:
            return Response(
                {'error': 'Contract not found or you cannot add milestones.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = MilestoneCreateSerializer(data=request.data)
        if serializer.is_valid():
            milestone = serializer.save(
                contract=contract,
                order=contract.milestones.count()
            )
            
            ContractActivity.objects.create(
                contract=contract,
                user=request.user,
                activity_type=ContractActivity.ActivityType.MILESTONE_ADDED,
                description=f'Added milestone: {milestone.title}'
            )
            
            return Response(
                MilestoneSerializer(milestone).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MilestoneActionView(APIView):
    """Handle milestone actions (start, submit, approve, revision)."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk, action):
        milestone = Milestone.objects.select_related('contract').filter(pk=pk).first()
        
        if not milestone:
            return Response(
                {'error': 'Milestone not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        contract = milestone.contract
        is_client = request.user == contract.client
        is_freelancer = request.user == contract.freelancer
        
        if action == 'start':
            if not is_freelancer or milestone.status != 'pending':
                return Response({'error': 'Cannot start this milestone.'}, status=status.HTTP_400_BAD_REQUEST)
            milestone.start()
            activity_type = ContractActivity.ActivityType.MILESTONE_STARTED
            description = f'Started working on: {milestone.title}'
            
        elif action == 'submit':
            if not is_freelancer or milestone.status not in ['in_progress', 'revision']:
                return Response({'error': 'Cannot submit this milestone.'}, status=status.HTTP_400_BAD_REQUEST)
            milestone.submit()
            activity_type = ContractActivity.ActivityType.MILESTONE_SUBMITTED
            description = f'Submitted milestone: {milestone.title}'
            
        elif action == 'approve':
            if not is_client or milestone.status != 'submitted':
                return Response({'error': 'Cannot approve this milestone.'}, status=status.HTTP_400_BAD_REQUEST)
            milestone.approve()
            activity_type = ContractActivity.ActivityType.MILESTONE_APPROVED
            description = f'Approved milestone: {milestone.title}'
            
        elif action == 'revision':
            if not is_client or milestone.status != 'submitted':
                return Response({'error': 'Cannot request revision.'}, status=status.HTTP_400_BAD_REQUEST)
            notes = request.data.get('notes', '')
            milestone.request_revision(notes)
            activity_type = ContractActivity.ActivityType.MILESTONE_REVISION
            description = f'Requested revision on: {milestone.title}'
            
        else:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
        
        ContractActivity.objects.create(
            contract=contract,
            user=request.user,
            activity_type=activity_type,
            description=description
        )
        
        return Response(MilestoneSerializer(milestone).data)


class ContractCompleteView(APIView):
    """Complete a contract."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        contract = Contract.objects.filter(
            pk=pk, client=request.user, status='active'
        ).first()
        
        if not contract:
            return Response(
                {'error': 'Contract not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        pending = contract.milestones.exclude(status__in=['approved', 'paid']).exists()
        if pending:
            return Response(
                {'error': 'Cannot complete contract. Some milestones are still pending.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contract.complete()
        
        ContractActivity.objects.create(
            contract=contract,
            user=request.user,
            activity_type=ContractActivity.ActivityType.CONTRACT_COMPLETED,
            description='Contract completed successfully'
        )
        
        return Response({'message': 'Contract completed successfully.'})
