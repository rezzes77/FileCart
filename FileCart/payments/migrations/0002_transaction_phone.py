# Generated by Django 5.1.6 on 2025-03-17 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
