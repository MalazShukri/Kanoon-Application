from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.login_student, name='login_student'),
    path('auth/verify-login/', views.verify_login_code, name='verify_login_code'),
    path('auth/signup/', views.signup_student, name='signup_student'),
    path('auth/verify-signup/', views.verify_signup_code, name='verify_signup_code'),
]
