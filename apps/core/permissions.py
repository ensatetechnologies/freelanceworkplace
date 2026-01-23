"""
Custom permissions for the application.
"""
from rest_framework import permissions


class IsFreelancer(permissions.BasePermission):
    """Allow access only to freelancers."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'freelancer'


class IsClient(permissions.BasePermission):
    """Allow access only to clients."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsProjectOwner(permissions.BasePermission):
    """Allow access only to project owner."""
    
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user


class IsProposalOwner(permissions.BasePermission):
    """Allow access only to proposal owner."""
    
    def has_object_permission(self, request, view, obj):
        return obj.freelancer == request.user


class IsContractParticipant(permissions.BasePermission):
    """Allow access to contract participants (client or freelancer)."""
    
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.client, obj.freelancer]


class IsConversationParticipant(permissions.BasePermission):
    """Allow access to conversation participants."""
    
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow write access only to the owner, read access to everyone."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
