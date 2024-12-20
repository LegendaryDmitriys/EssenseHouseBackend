# Generated by Django 5.1.2 on 2024-10-15 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_housecategory_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Скидка'),
        ),
        migrations.AddField(
            model_name='house',
            name='new',
            field=models.BooleanField(default=True, verbose_name='Новый продукт'),
        ),
        migrations.AddField(
            model_name='house',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Старая цена'),
        ),
    ]
