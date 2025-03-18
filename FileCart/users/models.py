from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


# Валидатор для проверки размера изображения
def validate_avatar_size(value):
    max_size_kb = 500  # Максимальный размер в килобайтах
    if value.size > max_size_kb * 1024:
        raise ValidationError(f"Размер файла слишком велик. Максимально: {max_size_kb}KB.")


# Поля для выбора пола
GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_avatar_size]
    )
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)  # Краткая информация
    date_of_birth = models.DateField(null=True, blank=True)  # Дата рождения
    address = models.CharField(max_length=255, blank=True)  # Адрес
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)  # Пол
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Баланс (сом)"
    )

    def __str__(self):
        return f"Profile of {self.user.username}"

