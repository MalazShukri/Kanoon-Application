from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *





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


# ---------------------- Generic API ---------------------
class GenericAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        self.model_name = getattr(self, 'model_name', '')
        return [perm() for perm in self.permission_classes]


# ---------------------- Student ----------------------

class StudentListCreateView(GenericAPIView):
    model_name = 'student'

    def get(self, request):
        if request.user.is_staff:
            students = Student.objects.all()
        else:
            students = Student.objects.filter(user=request.user)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class StudentDetailView(GenericAPIView):
    model_name = 'student'

    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        if not request.user.is_staff and student.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=403)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def patch(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        if not request.user.is_staff and student.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=403)
        serializer = StudentSerializer(
            student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        if not request.user.is_staff and student.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=403)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete.'}, status=403)
        student = get_object_or_404(Student, pk=pk)
        student.delete()
        return Response(status=204)


# ---------------------- Category ----------------------

class CategoryListCreateView(GenericAPIView):
    model_name = 'category'

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can create.'}, status=403)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CategoryDetailView(GenericAPIView):
    model_name = 'category'

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can update.'}, status=403)
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete.'}, status=403)
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=204)


# ---------------------- SubCategory ----------------------

class SubCategoryListCreateView(GenericAPIView):
    model_name = 'subcategory'

    def get(self, request):
        objs = SubCategory.objects.all()
        serializer = SubCategorySerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can create.'}, status=403)
        serializer = SubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class SubCategoryDetailView(GenericAPIView):
    model_name = 'subcategory'

    def get(self, request, pk):
        obj = get_object_or_404(SubCategory, pk=pk)
        serializer = SubCategorySerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can update.'}, status=403)
        obj = get_object_or_404(SubCategory, pk=pk)
        serializer = SubCategorySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete.'}, status=403)
        obj = get_object_or_404(SubCategory, pk=pk)
        obj.delete()
        return Response(status=204)


# ---------------------- Item ----------------------

class ItemListCreateView(GenericAPIView):
    model_name = 'item'

    def get(self, request):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can create.'}, status=403)
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ItemDetailView(GenericAPIView):
    model_name = 'item'

    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can update.'}, status=403)
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete.'}, status=403)
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        return Response(status=204)


# ---------------------- Question ----------------------

class QuestionListCreateView(GenericAPIView):
    model_name = 'question'

    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can create.'}, status=403)
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class QuestionDetailView(GenericAPIView):
    model_name = 'question'

    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can update.'}, status=403)
        question = get_object_or_404(Question, pk=pk)
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete.'}, status=403)
        question = get_object_or_404(Question, pk=pk)
        question.delete()
        return Response(status=204)


# ---------------------- Answer ----------------------

class AnswerListCreateView(GenericAPIView):
    model_name = 'answer'

    def get(self, request):
        answers = Answer.objects.all()
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can create.'}, status=403)
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AnswerDetailView(GenericAPIView):
    model_name = 'answer'

    def get(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = AnswerSerializer(answer)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can update.'}, status=403)
        answer = get_object_or_404(Answer, pk=pk)
        serializer = AnswerSerializer(answer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete.'}, status=403)
        answer = get_object_or_404(Answer, pk=pk)
        answer.delete()
        return Response(status=204)


# ---------------------- Payment ----------------------

class PaymentListCreateView(GenericAPIView):
    model_name = 'payment'

    def get(self, request):
        if request.user.is_staff:
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(student__user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PaymentDetailView(GenericAPIView):
    model_name = 'payment'

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if not request.user.is_staff and payment.student.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=403)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete.'}, status=403)
        payment = get_object_or_404(Payment, pk=pk)
        payment.delete()
        return Response(status=204)


# ---------------------- Notification ----------------------

class NotificationListCreateView(GenericAPIView):
    model_name = 'notification'

    def get(self, request):
        notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can create.'}, status=403)
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class NotificationDetailView(GenericAPIView):
    model_name = 'notification'

    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete.'}, status=403)
        notification = get_object_or_404(Notification, pk=pk)
        notification.delete()
        return Response(status=204)
