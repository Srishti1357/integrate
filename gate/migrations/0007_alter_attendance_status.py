# Generated by Django 5.1.6 on 2025-03-02 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gate', '0006_alter_attendance_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.IntegerField(choices=[(0, 'Rejected'), (1, 'Accepted'), (2, 'Pending')], default=2),
        ),
    ]
