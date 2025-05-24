from django.urls import path
from .views import *

urlpatterns = [
    path('auth/signup/', signup_student),
    path('auth/login/', login_student),
    path('auth/verify-login/', verify_login_code),
    path('auth/verify-signup/', verify_signup_code),

    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),

    path('subcategories/', SubCategoryListCreateView.as_view()),
    path('subcategories/<int:pk>/', SubCategoryDetailView.as_view()),

    path('items/', ItemListCreateView.as_view()),
    path('items/<int:pk>/', ItemDetailView.as_view()),

    path('questions/', QuestionListCreateView.as_view()),
    path('questions/<int:pk>/', QuestionDetailView.as_view()),

    path('answers/', AnswerListCreateView.as_view()),
    path('answers/<int:pk>/', AnswerDetailView.as_view()),

    path('students/', StudentListCreateView.as_view()),
    path('students/<int:pk>/', StudentDetailView.as_view()),

    path('payments/', PaymentListCreateView.as_view()),
    path('payments/<int:pk>/', PaymentDetailView.as_view()),

    path('notifications/', NotificationListCreateView.as_view()),
    path('notifications/<int:pk>/', NotificationDetailView.as_view()),
]
