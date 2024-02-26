# Generated by Django 5.0.1 on 2024-02-25 12:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_major'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultationrequest',
            name='user',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, related_name='consultation_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
