# Generated by Django 5.1.2 on 2024-10-17 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_alter_house_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
