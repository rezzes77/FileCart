from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название', unique=True)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    image = models.ImageField(upload_to='product-images/', verbose_name='Фото товара', blank=True, null=True)
    title = models.CharField(max_length=300, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    stock = models.PositiveIntegerField(verbose_name="Количество", null=True, blank=True)  # Новый параметр
    file = models.FileField(upload_to='files/', verbose_name='Файл товара', blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.SET_NULL, null=True,related_name='products')
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1, verbose_name='Пользователь',related_name='products')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')

    def __str__(self):
        return f"{self.title} - {self.price}, Количество: {self.stock} ({self.category.name if self.category else 'Uncategorized'}) by {self.user.username if self.user else 'Anonymous'}"