# Generated by Django 5.1.6 on 2025-03-01 14:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gate', '0003_alter_attendance_status_alter_attendance_student'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='student',
        ),
    ]
