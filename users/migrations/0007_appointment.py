# Generated by Django 5.0.1 on 2024-02-25 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_consultationrequest_major'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('time', models.CharField(blank=True, max_length=100)),
            ],
        ),
    ]
