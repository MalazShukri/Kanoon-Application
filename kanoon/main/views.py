from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import User, Student, PhoneVerification
from .serializers import (
    PhoneVerificationSerializer, PhoneNumberOnlySerializer, StudentSerializer, UserSignupSerializer, UserLoginSerializer
)
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

@api_view(['POST'])
@permission_classes([AllowAny])
def login_student(request):
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    phone_number = serializer.validated_data['phone_number']
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist. Please sign up.'}, status=status.HTTP_404_NOT_FOUND)
    # TODO: Call external API to get/send verification code
    verification_code = '0000'
    PhoneVerification.objects.update_or_create(
        phone_number=phone_number,
        defaults={'verification_code': verification_code, 'is_verified': False}
    )
    return Response({'message': 'Verification code sent'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_login_code(request):
    serializer = PhoneVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    phone_number = serializer.validated_data['phone_number']
    verification_code = serializer.validated_data['verification_code']
    try:
        verification = PhoneVerification.objects.get(phone_number=phone_number)
    except PhoneVerification.DoesNotExist:
        return Response({'error': 'No verification request found.'}, status=status.HTTP_404_NOT_FOUND)
    if verification.verification_code != verification_code:
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
    verification.is_verified = True
    verification.save()
    user = User.objects.get(phone_number=phone_number)
    refresh = RefreshToken.for_user(user)
    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_student(request):
    serializer = UserSignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    phone_number = serializer.validated_data['phone_number']
    if User.objects.filter(phone_number=phone_number).exists():
        return Response({'error': 'User already exists. Please login.'}, status=status.HTTP_400_BAD_REQUEST)
    # TODO: Call external API to get/send verification code
    verification_code = '0000'
    PhoneVerification.objects.update_or_create(
        phone_number=phone_number,
        defaults={'verification_code': verification_code, 'is_verified': False}
    )
    # Save the student data temporarily in the session or require it again after verification
    signup_data = {
        'phone_number': phone_number,
        'full_name': serializer.validated_data.get('full_name'),
        'gender': serializer.validated_data.get('gender'),
        'birth_date': str(serializer.validated_data.get('birth_date')) if serializer.validated_data.get('birth_date') else '',
    }
    # Handle photo upload
    photo = request.FILES.get('photo')
    if photo:
        from django.core.files.storage import default_storage
        photo_path = default_storage.save(f"student_photos/{photo.name}", photo)
        signup_data['photo'] = photo_path
    else:
        signup_data['photo'] = ''
    request.session['signup_data'] = signup_data
    return Response({'message': 'Verification code sent'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_signup_code(request):
    serializer = PhoneVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    phone_number = serializer.validated_data['phone_number']
    verification_code = serializer.validated_data['verification_code']
    try:
        verification = PhoneVerification.objects.get(phone_number=phone_number)
    except PhoneVerification.DoesNotExist:
        return Response({'error': 'No verification request found.'}, status=status.HTTP_404_NOT_FOUND)
    if verification.verification_code != verification_code:
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
    verification.is_verified = True
    verification.save()
    # Retrieve student data from session
    signup_data = request.session.get('signup_data')
    if not signup_data or signup_data['phone_number'] != phone_number:
        return Response({'error': 'No signup data found. Please sign up again.'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create(phone_number=phone_number)
    student = Student(
        user=user,
        full_name=signup_data['full_name'],
        gender=signup_data['gender'],
        birth_date=signup_data['birth_date'] if signup_data['birth_date'] else None,
    )
    # Attach photo if uploaded
    if signup_data.get('photo'):
        student.photo = signup_data['photo']
    student.save()
    refresh = RefreshToken.for_user(user)
    # Clear session after signup
    del request.session['signup_data']
    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
