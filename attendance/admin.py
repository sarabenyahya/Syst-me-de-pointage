from django.contrib import admin

from .models import Department, Employee, Attendance

admin.site.register(Department)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'department', 'position')
    list_filter = ('department', 'position')
    search_fields = ('first_name', 'last_name', 'department__name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'timestamp']
