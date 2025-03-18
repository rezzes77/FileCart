from django.db import models
from users.models import Profile


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма (сом)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    code = models.CharField(max_length=6, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # Код подтверждения
    created_at = models.DateTimeField(auto_now_add=True)