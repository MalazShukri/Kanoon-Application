from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import User, PhoneVerification
from django.core.files.storage import default_storage
import json

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def request_phone_verification(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create or update verification code (static 0000 for now)
    verification, created = PhoneVerification.objects.update_or_create(
        phone_number=phone_number,
        defaults={
            'verification_code': '0000',
            'is_verified': False
        }
    )
    
    # In real implementation, send SMS here
    return Response({'message': 'Verification code sent'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone(request):
    phone_number = request.data.get('phone_number')
    verification_code = request.data.get('verification_code')
    
    try:
        verification = PhoneVerification.objects.get(
            phone_number=phone_number,
            verification_code=verification_code,
            is_verified=False
        )
    except PhoneVerification.DoesNotExist:
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark as verified
    verification.is_verified = True
    verification.save()
    
    # Create or get user
    user, created = User.objects.get_or_create(phone_number=phone_number)
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'is_profile_complete': bool(user.full_name)  # Check if profile is complete
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_profile(request):
    user = request.user
    
    # Get data from request
    full_name = request.data.get('full_name')
    gender = request.data.get('gender')
    birth_date = request.data.get('birth_date')
    photo = request.FILES.get('photo')
    
    # Validate required fields
    if not all([full_name, gender, birth_date]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update user profile
    user.full_name = full_name
    user.gender = gender
    user.birth_date = birth_date
    if photo:
        # Save photo and update user
        file_name = default_storage.save(f'user_photos/{user.id}_{photo.name}', photo)
        user.photo = file_name
    
    user.is_verified = True
    user.save()
    
    return Response({'message': 'Profile completed successfully'}, status=status.HTTP_200_OK)
