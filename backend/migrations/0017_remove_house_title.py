# Generated by Django 5.1.2 on 2024-10-17 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_alter_house_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='house',
            name='title',
        ),
    ]
