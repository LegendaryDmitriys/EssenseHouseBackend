# Generated by Django 5.1.2 on 2024-10-15 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_housecategory_house_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='houses/'),
        ),
    ]
