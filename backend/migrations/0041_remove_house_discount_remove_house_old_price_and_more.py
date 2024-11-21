# Generated by Django 5.1.3 on 2024-11-20 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0040_remove_document_house_house_documents'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='house',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='house',
            name='old_price',
        ),
        migrations.AddField(
            model_name='house',
            name='discount_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Скидка (%)'),
        ),
    ]