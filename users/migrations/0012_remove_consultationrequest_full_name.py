# Generated by Django 5.0.1 on 2024-01-15 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_consultationrequest_faculty_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consultationrequest',
            name='full_name',
        ),
    ]
