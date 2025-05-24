from rest_framework import serializers
from .models import *

class PhoneVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVerification
        fields = ['phone_number', 'verification_code']
        extra_kwargs = {
            'verification_code': {'write_only': True}
        }

class PhoneNumberOnlySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class UserSignupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    full_name = serializers.CharField(max_length=255)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')])
    birth_date = serializers.DateField(required=False)
    photo = serializers.ImageField(required=False)

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.full_name', read_only=True)
    student_id = serializers.CharField(
        source='student.user.id', read_only=True)
    subject = serializers.CharField(source='item.title', read_only=True)
    subcategory = serializers.CharField(
        source='item.subcategory.title', read_only=True)
    category = serializers.CharField(
        source='item.subcategory.category.title', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'student_id', 'student_name', 'category',
                  'subcategory', 'subject', 'amount', 'date']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'date', 'time']
