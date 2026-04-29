from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, timedelta


@login_required
def dashboard(request):
    from apps.patients.models import Patient
    from apps.appointments.models import Appointment
    from apps.pharmacy.models import Medicine
    from apps.finance.models import Transaction

    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == 'patient':
        return redirect('patient_portal')

    today = date.today()

    total_patients    = Patient.objects.count()
    today_appts       = Appointment.objects.filter(date=today).count()
    low_stock         = Medicine.objects.filter(quantity__lt=10).count()
    today_income      = Transaction.objects.filter(date=today, transaction_type='income').aggregate(t=Sum('amount'))['t'] or 0
    today_expense     = Transaction.objects.filter(date=today, transaction_type='expense').aggregate(t=Sum('amount'))['t'] or 0
    recent_appts      = Appointment.objects.filter(date=today).select_related('patient','doctor').order_by('time')[:8]
    low_stock_meds    = Medicine.objects.filter(quantity__lt=10).order_by('quantity')[:5]

    week_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        inc = Transaction.objects.filter(date=d, transaction_type='income').aggregate(t=Sum('amount'))['t'] or 0
        exp = Transaction.objects.filter(date=d, transaction_type='expense').aggregate(t=Sum('amount'))['t'] or 0
        week_data.append({'day': d.strftime('%a'), 'income': float(inc), 'expense': float(exp)})

    return render(request, 'dashboard.html', {
        'total_patients': total_patients, 'today_appointments': today_appts,
        'low_stock': low_stock, 'today_income': today_income,
        'today_expense': today_expense, 'net': today_income - today_expense,
        'recent_appointments': recent_appts, 'low_stock_meds': low_stock_meds,
        'week_data': week_data, 'today': today,
    })


@login_required
def patient_portal(request):
    from apps.patients.models import Patient
    from apps.appointments.models import Appointment
    from apps.pharmacy.models import Prescription

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    context = {'patient': patient}
    if patient:
        context['appointments'] = Appointment.objects.filter(patient=patient).order_by('-date')[:10]
        context['prescriptions'] = Prescription.objects.filter(patient=patient).order_by('-date')[:5]
    return render(request, 'patient_portal.html', context)
