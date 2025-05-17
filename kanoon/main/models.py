from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, username=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required')
        user = self.model(phone_number=phone_number, username=username, **extra_fields)
        user.set_unusable_password() 
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if not username:
            raise ValueError('Superuser must have a username')
        if not password:
            raise ValueError('Superuser must have a password')
        user = self.model(phone_number=phone_number, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.username if self.username else self.phone_number

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)

    def __str__(self):
        return self.full_name

class PhoneVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    verification_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number} - {self.is_verified}"

class Category(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.title

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='subcategory_images/')

    def __str__(self):
        return f"{self.category.title} - {self.title}"


class Item(models.Model):
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='item_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.subcategory.title} - {self.title}"


class Question(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f"Question for {self.item.title}: {self.text}"


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    option_label = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
    )
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} - {self.option_label}: {self.answer_text}"


class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.item.title} - {self.amount}$"


class Notification(models.Model):
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:50]
