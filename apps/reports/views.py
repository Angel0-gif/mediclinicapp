from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import date, timedelta
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.pharmacy.models import Medicine, StockMovement
from apps.finance.models import Transaction

@login_required
def reports_home(request):
    return render(request,'reports/home.html')

@login_required
def financial_report(request):
    start = request.GET.get('start', str(date.today().replace(day=1)))
    end   = request.GET.get('end',   str(date.today()))
    txns  = Transaction.objects.filter(date__gte=start, date__lte=end)
    S     = lambda qs: qs.aggregate(t=Sum('amount'))['t'] or 0
    daily = []
    s, e  = date.fromisoformat(start), date.fromisoformat(end)
    cur   = s
    while cur <= e:
        inc = S(txns.filter(date=cur,transaction_type='income'))
        exp = S(txns.filter(date=cur,transaction_type='expense'))
        daily.append({'date':str(cur),'income':float(inc),'expense':float(exp),'net':float(inc-exp)})
        cur += timedelta(days=1)
    return render(request,'reports/financial.html',{
        'start':start,'end':end,
        'total_in':  S(txns.filter(transaction_type='income')),
        'total_out': S(txns.filter(transaction_type='expense')),
        'net':       S(txns.filter(transaction_type='income'))-S(txns.filter(transaction_type='expense')),
        'income_by_cat':  txns.filter(transaction_type='income').values('category__name').annotate(total=Sum('amount')).order_by('-total'),
        'expense_by_cat': txns.filter(transaction_type='expense').values('category__name').annotate(total=Sum('amount')).order_by('-total'),
        'daily': daily,
    })

@login_required
def pharmacy_report(request):
    today = date.today()
    return render(request,'reports/pharmacy.html',{
        'low_stock':  Medicine.objects.filter(quantity__lt=10).order_by('quantity'),
        'expiring':   Medicine.objects.filter(expiry_date__lte=today+timedelta(days=30),expiry_date__gte=today).order_by('expiry_date'),
        'expired':    Medicine.objects.filter(expiry_date__lt=today),
        'movements':  StockMovement.objects.select_related('medicine','performed_by').order_by('-date')[:50],
    })

@login_required
def patient_report(request):
    return render(request,'reports/patients.html',{
        'total':        Patient.objects.count(),
        'by_gender':    Patient.objects.values('gender').annotate(count=Count('id')),
        'by_blood':     Patient.objects.values('blood_group').annotate(count=Count('id')),
        'new_month':    Patient.objects.filter(registered_at__gte=date.today().replace(day=1)).count(),
    })
