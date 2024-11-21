# Generated by Django 5.1.2 on 2024-10-29 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0030_remove_filter_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilterOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('field_name', models.CharField(max_length=50, verbose_name='Имя поля из модели House')),
                ('filter_type', models.CharField(choices=[('exact', 'Точное совпадение'), ('range', 'Диапазон'), ('contains', 'Содержит')], max_length=50)),
                ('options', models.JSONField(default=dict)),
            ],
        ),
        migrations.DeleteModel(
            name='Filter',
        ),
    ]