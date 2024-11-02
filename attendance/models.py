import os
from django.contrib.auth.models import AbstractUser
from django.db import models


def user_directory_path(instance, filename):
    # Extract the file extension
    extension = filename.split('.')[-1]
    # Construct the new filename using the username
    filename = f"{instance.get_full_name()}.{extension}"
    # Return the full path to the file
    return os.path.join('employees', filename)


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)
    hire_date = models.DateField(auto_now_add=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    insurance_number = models.CharField(max_length=50)
    photo = models.ImageField(upload_to=user_directory_path)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.get_full_name(),
            "department": self.department.name,
            "position": self.position,
            "insurance_number": self.insurance_number,
            "photo": self.photo.url
        }


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.timestamp}"
