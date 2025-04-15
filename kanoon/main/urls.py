from django.urls import path
from . import views

urlpatterns = [
    path('auth/request-verification/', views.request_phone_verification, name='request_verification'),
    path('auth/verify-phone/', views.verify_phone, name='verify_phone'),
    path('auth/complete-profile/', views.complete_profile, name='complete_profile'),
]
