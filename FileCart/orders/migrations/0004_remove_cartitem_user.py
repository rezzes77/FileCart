# Generated by Django 5.1.6 on 2025-03-14 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_cartitem_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='user',
        ),
    ]
