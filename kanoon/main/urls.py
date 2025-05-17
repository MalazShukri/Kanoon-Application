from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'subcategories', views.SubCategoryViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'answers', views.AnswerViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'notifications', views.NotificationViewSet)


urlpatterns = [
    path('auth/signup/', views.signup_student, name='signup_student'),
    path('auth/login/', views.login_student, name='login_student'),
    path('auth/verify-login/', views.verify_login_code, name='verify_login_code'),
    path('auth/verify-signup/', views.verify_signup_code,
         name='verify_signup_code'),
    path('', include(router.urls)),  
]
