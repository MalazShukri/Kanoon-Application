from rest_framework import serializers
from .models import User, Student, PhoneVerification

class PhoneVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVerification
        fields = ['phone_number', 'verification_code']
        extra_kwargs = {
            'verification_code': {'write_only': True}
        }

class PhoneNumberOnlySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['full_name', 'gender', 'birth_date', 'photo']

    def validate_gender(self, value):
        if value not in ['male', 'female']:
            raise serializers.ValidationError("Gender must be either 'male' or 'female'")
        return value

    def validate_birth_date(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Birth date cannot be in the future")
        return value

class UserSignupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    full_name = serializers.CharField(max_length=255)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')])
    birth_date = serializers.DateField(required=False)
    photo = serializers.ImageField(required=False)

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
