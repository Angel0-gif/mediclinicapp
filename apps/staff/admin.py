from django.contrib import admin
from .models import StaffProfile, Attendance, PayrollRecord
admin.site.register(StaffProfile)
admin.site.register(Attendance)
admin.site.register(PayrollRecord)
