from django.urls import path
from . import views
urlpatterns = [
    path('',                      views.staff_list,        name='staff_list'),
    path('<int:pk>/',             views.staff_detail,      name='staff_detail'),
    path('attendance/',           views.attendance_today,  name='attendance_today'),
    path('payroll/',              views.payroll_list,      name='payroll_list'),
    path('payroll/generate/',     views.generate_payroll,  name='generate_payroll'),
    path('payroll/<int:pk>/paid/',views.mark_payroll_paid, name='mark_payroll_paid'),
]
