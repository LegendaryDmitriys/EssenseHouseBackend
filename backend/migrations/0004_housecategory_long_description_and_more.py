# Generated by Django 5.1.2 on 2024-10-15 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_house_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='housecategory',
            name='long_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='housecategory',
            name='short_description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
