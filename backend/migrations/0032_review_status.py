# Generated by Django 5.1.2 on 2024-11-04 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0031_filteroption_delete_filter'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='status',
            field=models.CharField(choices=[('published', 'Опубликован'), ('pending', 'Ожидает публикации'), ('rejected', 'Отказано')], default='pending', max_length=10),
        ),
    ]
