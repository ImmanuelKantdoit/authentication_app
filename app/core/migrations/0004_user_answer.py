# Generated by Django 4.0.10 on 2023-11-15 07:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_exam_question_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_answer', models.TextField(max_length=255)),
                ('iscorrect', models.BooleanField()),
                ('issubmitted', models.BooleanField()),
                ('isbookmarked', models.BooleanField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.exam_question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
