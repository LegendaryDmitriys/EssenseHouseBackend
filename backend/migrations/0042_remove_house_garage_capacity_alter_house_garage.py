# Generated by Django 5.1.3 on 2024-11-20 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0041_remove_house_discount_remove_house_old_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='house',
            name='garage_capacity',
        ),
        migrations.AlterField(
            model_name='house',
            name='garage',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Гараж (кол-во машин)'),
        ),
    ]