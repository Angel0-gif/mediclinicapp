from django.urls import path
from . import views
urlpatterns = [
    path('',              views.appointment_list,          name='appointment_list'),
    path('new/',          views.appointment_create,        name='appointment_create'),
    path('<int:pk>/',     views.appointment_detail,        name='appointment_detail'),
    path('<int:pk>/status/', views.appointment_update_status, name='appointment_update_status'),
]
