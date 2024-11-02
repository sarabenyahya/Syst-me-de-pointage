import os
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Employee, Department
from django.conf import settings

class Command(BaseCommand):
    help = 'Fetch and populate employees data'

    def handle(self, *args, **kwargs):
        self.populate_departments()
        self.populate_employees()

    def populate_departments(self):
        departments = ['HR', 'Engineering', 'Marketing', 'Sales']
        for dept_name in departments:
            Department.objects.get_or_create(name=dept_name)
        self.stdout.write(self.style.SUCCESS('Successfully populated departments'))

    def populate_employees(self):
        url = 'https://randomuser.me/api/?results=10'
        response = requests.get(url)
        data = response.json()

        for result in data['results']:
            user = User.objects.create_user(
                username=result['login']['username'],
                first_name=result['name']['first'],
                last_name=result['name']['last'],
                email=result['email'],
                password='password123'  # Change as necessary
            )

            department = Department.objects.order_by('?').first()
            photo_url = result['picture']['large']
            photo_response = requests.get(photo_url)
            photo_content = ContentFile(photo_response.content)
            photo_filename = f"{result['login']['username']}.jpg"

            employee = Employee.objects.create(
                user=user,
                hire_date=result['registered']['date'][:10],
                department=department,
                position='Employee',  # Default position
                insurance_number=result['id']['value']
            )
            employee.photo.save(photo_filename, photo_content, save=True)

        self.stdout.write(self.style.SUCCESS('Successfully populated employees'))
