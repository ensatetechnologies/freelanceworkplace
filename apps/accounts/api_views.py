"""
API views for accounts app.
"""
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout

from .models import User, FreelancerProfile, ClientProfile
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer,
    FreelancerProfileSerializer,
    ClientProfileSerializer,
    PublicUserSerializer
)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Registration successful. Please check your email for verification.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    """User login endpoint."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Login successful.',
                'user': UserSerializer(user).data
            })
        
        return Response({
            'error': 'Invalid credentials.'
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    """User logout endpoint."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful.'})


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get/Update current user endpoint."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get/Update user profile endpoint."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.user.role == 'freelancer':
            return FreelancerProfileSerializer
        return ClientProfileSerializer
    
    def get_object(self):
        user = self.request.user
        if user.role == 'freelancer':
            profile, _ = FreelancerProfile.objects.get_or_create(user=user)
            return profile
        profile, _ = ClientProfile.objects.get_or_create(user=user)
        return profile


class PublicProfileView(generics.RetrieveAPIView):
    """Get public user profile endpoint."""
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        user = self.get_object()
        if user.role == 'freelancer':
            return FreelancerProfileSerializer
        return ClientProfileSerializer
    
    def get_object(self):
        user = super().get_object()
        return user.get_profile()


class FreelancerListView(generics.ListAPIView):
    """List freelancers endpoint."""
    permission_classes = [AllowAny]
    serializer_class = FreelancerProfileSerializer
    
    def get_queryset(self):
        queryset = FreelancerProfile.objects.select_related('user').filter(
            user__is_profile_complete=True
        )
        
        skill = self.request.query_params.get('skill')
        if skill:
            queryset = queryset.filter(skills__contains=skill)
        
        availability = self.request.query_params.get('availability')
        if availability:
            queryset = queryset.filter(availability=availability)
        
        return queryset.order_by('-avg_rating')
