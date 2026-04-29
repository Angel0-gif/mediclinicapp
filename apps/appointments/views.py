from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import Appointment
from apps.patients.models import Patient
from django.contrib.auth.models import User

@login_required
def appointment_list(request):
    filter_date = request.GET.get('date', str(date.today()))
    status = request.GET.get('status','')
    qs = Appointment.objects.select_related('patient','doctor')
    if filter_date: qs = qs.filter(date=filter_date)
    if status:      qs = qs.filter(status=status)
    return render(request,'appointments/list.html',{
        'appointments': qs.order_by('time'),
        'filter_date': filter_date, 'status': status,
        'patients': Patient.objects.filter(is_active=True).order_by('first_name'),
        'doctors':  User.objects.filter(profile__role='doctor'),
        'status_choices': Appointment.STATUS_CHOICES,
    })

@login_required
def appointment_create(request):
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        did = request.POST.get('doctor')
        Appointment.objects.create(
            patient=patient,
            doctor=User.objects.get(pk=did) if did else None,
            date=request.POST['date'], time=request.POST['time'],
            appointment_type=request.POST.get('appointment_type','consultation'),
            reason=request.POST.get('reason',''), notes=request.POST.get('notes',''),
        )
        messages.success(request,'Appointment scheduled.')
        return redirect('appointment_list')
    return render(request,'appointments/form.html',{
        'patients': Patient.objects.filter(is_active=True).order_by('first_name'),
        'doctors':  User.objects.filter(profile__role='doctor'),
        'today': str(date.today()),
    })

@login_required
def appointment_update_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appt.status = request.POST.get('status', appt.status)
        appt.notes  = request.POST.get('notes',  appt.notes)
        appt.save()
        messages.success(request,'Appointment updated.')
    return redirect('appointment_list')

@login_required
def appointment_detail(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    return render(request,'appointments/detail.html',{'appt':appt})
