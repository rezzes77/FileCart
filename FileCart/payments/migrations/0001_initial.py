# Generated by Django 5.1.6 on 2025-03-17 12:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0003_profile_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма (сом)')),
                ('status', models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('success', 'Успешно'), ('failed', 'Ошибка')], default='pending', max_length=10)),
                ('code', models.CharField(blank=True, max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='users.profile')),
            ],
        ),
    ]
