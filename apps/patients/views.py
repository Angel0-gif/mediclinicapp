from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Patient, MedicalRecord
from django.contrib.auth.models import User
from apps.core.models import UserProfile


@login_required
def patient_list(request):
    q = request.GET.get('q','')
    patients = Patient.objects.filter(is_active=True)
    if q:
        patients = patients.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(phone__icontains=q))
    return render(request,'patients/list.html',{'patients':patients,'q':q})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    from apps.appointments.models import Appointment
    from apps.pharmacy.models import Prescription
    from apps.finance.models import Bill
    return render(request,'patients/detail.html',{
        'patient': patient,
        'records': patient.records.all()[:10],
        'appointments': Appointment.objects.filter(patient=patient).order_by('-date')[:5],
        'prescriptions': Prescription.objects.filter(patient=patient).order_by('-date')[:5],
        'bills': Bill.objects.filter(patient=patient).order_by('-created_at')[:5],
    })


@login_required
def patient_create(request):
    if request.method == 'POST':
        p = Patient(
            first_name=request.POST['first_name'], last_name=request.POST['last_name'],
            date_of_birth=request.POST['date_of_birth'], gender=request.POST['gender'],
            blood_group=request.POST.get('blood_group',''), phone=request.POST['phone'],
            email=request.POST.get('email',''), address=request.POST.get('address',''),
            emergency_contact_name=request.POST.get('emergency_contact_name',''),
            emergency_contact_phone=request.POST.get('emergency_contact_phone',''),
            allergies=request.POST.get('allergies',''),
            chronic_conditions=request.POST.get('chronic_conditions',''),
            notes=request.POST.get('notes',''),
        )
        if request.POST.get('create_account'):
            uname = request.POST.get('username','').strip()
            pwd   = request.POST.get('password','').strip()
            if uname and pwd:
                if User.objects.filter(username=uname).exists():
                    messages.error(request,'Username already taken.')
                    return render(request,'patients/form.html',{'form_data':request.POST})
                u = User.objects.create_user(username=uname,password=pwd,
                    first_name=p.first_name,last_name=p.last_name,email=p.email)
                UserProfile.objects.filter(user=u).update(role='patient',phone=p.phone)
                p.user = u
        p.save()
        messages.success(request,f'Patient {p.full_name} registered.')
        return redirect('patient_detail',pk=p.pk)
    return render(request,'patients/form.html',{})


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        for f in ['first_name','last_name','date_of_birth','gender','blood_group',
                  'phone','email','address','emergency_contact_name',
                  'emergency_contact_phone','allergies','chronic_conditions','notes']:
            setattr(patient, f, request.POST.get(f, getattr(patient, f)))
        patient.save()
        messages.success(request,'Patient updated.')
        return redirect('patient_detail',pk=pk)
    return render(request,'patients/form.html',{'patient':patient})


@login_required
def medical_record_create(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk)
    if request.method == 'POST':
        MedicalRecord.objects.create(
            patient=patient, doctor=request.user,
            chief_complaint=request.POST['chief_complaint'],
            diagnosis=request.POST['diagnosis'],
            treatment=request.POST['treatment'],
            notes=request.POST.get('notes',''),
            follow_up_date=request.POST.get('follow_up_date') or None,
        )
        messages.success(request,'Medical record added.')
        return redirect('patient_detail',pk=patient_pk)
    return render(request,'patients/record_form.html',{'patient':patient})
