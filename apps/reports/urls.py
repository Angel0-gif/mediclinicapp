from django.urls import path
from . import views
urlpatterns = [
    path('',          views.reports_home,       name='reports_home'),
    path('financial/', views.financial_report,  name='financial_report'),
    path('pharmacy/',  views.pharmacy_report,   name='pharmacy_report'),
    path('patients/',  views.patient_report,    name='patient_report'),
]
