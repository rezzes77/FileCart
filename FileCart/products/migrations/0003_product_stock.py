# Generated by Django 5.1.6 on 2025-03-14 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_category_description_product_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество'),
        ),
    ]
