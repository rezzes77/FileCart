from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import random

def validate_avatar_size(value):
    max_size_kb = 500
    if value.size > max_size_kb * 1024:
        raise ValidationError(f"Размер файла слишком велик. Максимально: {max_size_kb}KB.")

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_avatar_size]
    )
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Баланс (сом)")
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    active_promo = models.ForeignKey(
        'promocode.PromoCode',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    def __str__(self):
        return f"Profile of {self.user.username}"

    def generate_confirmation_code(self, amount):
        """Генерирует код подтверждения и сохраняет сумму"""
        self.confirmation_code = str(random.randint(100000, 999999))
        self.pending_amount = amount
        self.save()
