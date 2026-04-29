from django.urls import path
from . import views
urlpatterns = [
    path('',                            views.finance_dashboard, name='finance_dashboard'),
    path('transactions/',               views.transaction_list,  name='transaction_list'),
    path('transactions/new/',           views.transaction_create,name='transaction_create'),
    path('bills/',                      views.bill_list,         name='bill_list'),
    path('bills/new/',                  views.bill_create,       name='bill_create'),
    path('bills/new/<int:patient_pk>/', views.bill_create,       name='bill_create_for_patient'),
    path('bills/<int:pk>/',             views.bill_detail,       name='bill_detail'),
]
