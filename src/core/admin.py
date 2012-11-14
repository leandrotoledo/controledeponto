from django.contrib import admin

from core.models import Employee, EmployeeTracking, EmployeeTotalHours


admin.site.register(Employee)
admin.site.register(EmployeeTracking)
admin.site.register(EmployeeTotalHours)
