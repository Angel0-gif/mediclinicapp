from django.urls import path
from . import views
urlpatterns = [
    path('',                                      views.medicine_list,       name='medicine_list'),
    path('new/',                                  views.medicine_create,     name='medicine_create'),
    path('<int:pk>/edit/',                        views.medicine_edit,       name='medicine_edit'),
    path('<int:pk>/stock/',                       views.stock_movement,      name='stock_movement'),
    path('history/',                              views.stock_history,       name='stock_history'),
    path('prescriptions/',                        views.prescription_list,   name='prescription_list'),
    path('prescriptions/new/',                    views.prescription_create, name='prescription_create'),
    path('prescriptions/new/<int:patient_pk>/',   views.prescription_create, name='prescription_create_for_patient'),
    path('prescriptions/<int:pk>/dispense/',      views.dispense_prescription, name='dispense_prescription'),
]
