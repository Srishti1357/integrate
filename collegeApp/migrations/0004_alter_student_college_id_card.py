# Generated by Django 5.1.6 on 2025-03-01 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collegeApp', '0003_alter_student_college'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='college_id_card',
            field=models.ImageField(blank=True, null=True, upload_to='college_id_cards/'),
        ),
    ]
