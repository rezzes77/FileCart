from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Код")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Минимальная сумма заказа"
    )
    discount_percent = models.PositiveIntegerField(verbose_name="Процент скидки")
    max_uses = models.PositiveIntegerField(verbose_name="Максимальное количество использований")
    current_uses = models.PositiveIntegerField(default=0, verbose_name="Текущее количество использований")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

    @property
    def is_valid(self):
        return (
                self.is_active and
                self.current_uses < self.max_uses and
                timezone.now() <= self.end_date
        )


class PromoCodeUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="promo_usages")
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'promo_code')