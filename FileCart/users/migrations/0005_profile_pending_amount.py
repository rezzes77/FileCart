# Generated by Django 5.1.6 on 2025-03-19 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile_confirmation_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pending_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
