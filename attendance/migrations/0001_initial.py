# Generated by Django 5.0.6 on 2024-05-31 15:36

import attendance.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=100)),
                ('hire_date', models.DateField(auto_now_add=True)),
                ('position', models.CharField(max_length=100)),
                ('insurance_number', models.CharField(max_length=50)),
                ('photo', models.ImageField(upload_to=attendance.models.user_directory_path)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.department')),
            ],
            options={
                'verbose_name': 'Employé',
                'verbose_name_plural': 'Employés',
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.employee')),
            ],
        ),
    ]
