# Generated by Django 5.1.2 on 2024-11-06 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0032_review_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquestion',
            name='status',
            field=models.CharField(choices=[('waiting', 'Ожидает ответа'), ('answered', 'Ответ предоставлен'), ('closed', 'Закрыт')], default='waiting', max_length=10),
        ),
    ]
