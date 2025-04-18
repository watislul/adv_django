from rest_framework import status, viewsets, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    ChangePasswordSerializer, ProfileUpdateSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ProfileSerializer
)


User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a profile or admins to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is admin
        if request.user.is_staff:
            return True
        
        # Check if obj is the user's own profile
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class RegisterView(generics.CreateAPIView):
    """View for user registration."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                # Send verification email (would be implemented in a real app)
                # send_verification_email(user)
                
                # Return tokens for auto-login
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """View for user login."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """View for changing user password."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Old password is incorrect'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {'message': 'Password successfully changed'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_object(self):
        return self.request.user.profile
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ProfileUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(ProfileSerializer(instance).data)


class PasswordResetRequestView(APIView):
    """View for requesting a password reset."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate token
                token = get_random_string(32)
                # In a real app, this would be stored securely and expire after a time period
                # user.password_reset_token = token
                # user.password_reset_expires = timezone.now() + timezone.timedelta(hours=24)
                # user.save()
                
                # Send email with reset link
                # reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
                # send_mail(
                #     'Password Reset Request',
                #     f'Click the link to reset your password: {reset_link}',
                #     settings.DEFAULT_FROM_EMAIL,
                #     [email],
                #     fail_silently=False,
                # )
                
                return Response(
                    {'message': 'Password reset email sent'},
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                # Return success even if user doesn't exist for security
                return Response(
                    {'message': 'Password reset email sent'},
                    status=status.HTTP_200_OK
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """View for confirming a password reset."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            # In a real app, this would validate the token and expiry
            # try:
            #     user = User.objects.get(password_reset_token=token)
            #     if user.password_reset_expires > timezone.now():
            #         user.set_password(password)
            #         user.password_reset_token = None
            #         user.password_reset_expires = None
            #         user.save()
            #         return Response(
            #             {'message': 'Password reset successful'},
            #             status=status.HTTP_200_OK
            #         )
            #     else:
            #         return Response(
            #             {'error': 'Token has expired'},
            #             status=status.HTTP_400_BAD_REQUEST
            #         )
            # except User.DoesNotExist:
            #     pass
            
            # For demo purposes
            return Response(
                {'message': 'Password reset successful'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """View for verifying user email."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        # In a real app, this would validate the verification token
        # try:
        #     user = User.objects.get(verification_token=token)
        #     if not user.is_email_verified:
        #         user.is_email_verified = True
        #         user.verification_token = None
        #         user.save()
        #         return Response(
        #             {'message': 'Email verification successful'},
        #             status=status.HTTP_200_OK
        #         )
        #     else:
        #         return Response(
        #             {'message': 'Email already verified'},
        #             status=status.HTTP_200_OK
        #         )
        # except User.DoesNotExist:
        #     return Response(
        #         {'error': 'Invalid verification token'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        # For demo purposes
        return Response(
            {'message': 'Email verification successful'},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user details (admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]