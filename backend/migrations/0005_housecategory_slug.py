# Generated by Django 5.1.2 on 2024-10-15 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_housecategory_long_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='housecategory',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
