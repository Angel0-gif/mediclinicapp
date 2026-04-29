from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Medicine, StockMovement, Prescription, PrescriptionItem, MedicineCategory
from apps.patients.models import Patient

@login_required
def medicine_list(request):
    q    = request.GET.get('q','')
    cat  = request.GET.get('category','')
    meds = Medicine.objects.filter(is_active=True)
    if q:   meds = meds.filter(Q(name__icontains=q)|Q(generic_name__icontains=q))
    if cat: meds = meds.filter(category__id=cat)
    return render(request,'pharmacy/medicine_list.html',{
        'meds': meds, 'categories': MedicineCategory.objects.all(),
        'q': q, 'sel_cat': cat,
    })

@login_required
def medicine_create(request):
    categories = MedicineCategory.objects.all()
    if request.method == 'POST':
        cat_id = request.POST.get('category')
        med = Medicine.objects.create(
            name=request.POST['name'],
            generic_name=request.POST.get('generic_name',''),
            category_id=cat_id if cat_id else None,
            unit=request.POST.get('unit','tablet'),
            quantity=0,
            min_stock=int(request.POST.get('min_stock',10)),
            purchase_price=request.POST.get('purchase_price',0),
            selling_price=request.POST.get('selling_price',0),
            expiry_date=request.POST.get('expiry_date') or None,
            manufacturer=request.POST.get('manufacturer',''),
            description=request.POST.get('description',''),
        )
        init_qty = int(request.POST.get('quantity',0))
        if init_qty > 0:
            StockMovement.objects.create(
                medicine=med, movement_type='adjustment', quantity=init_qty,
                performed_by=request.user, reason='Initial stock'
            )
        messages.success(request, f'{med.name} added to inventory.')
        return redirect('medicine_list')
    return render(request,'pharmacy/medicine_form.html',{'categories':categories})

@login_required
def medicine_edit(request, pk):
    med        = get_object_or_404(Medicine, pk=pk)
    categories = MedicineCategory.objects.all()
    if request.method == 'POST':
        med.name           = request.POST['name']
        med.generic_name   = request.POST.get('generic_name','')
        cat_id             = request.POST.get('category')
        med.category_id    = cat_id if cat_id else None
        med.unit           = request.POST.get('unit','tablet')
        med.min_stock      = int(request.POST.get('min_stock',10))
        med.purchase_price = request.POST.get('purchase_price',0)
        med.selling_price  = request.POST.get('selling_price',0)
        med.expiry_date    = request.POST.get('expiry_date') or None
        med.manufacturer   = request.POST.get('manufacturer','')
        med.description    = request.POST.get('description','')
        med.save()
        messages.success(request,'Medicine updated.')
        return redirect('medicine_list')
    return render(request,'pharmacy/medicine_form.html',{'med':med,'categories':categories})

@login_required
def stock_movement(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        move_type = request.POST['movement_type']
        qty       = int(request.POST['quantity'])
        if move_type == 'out' and qty > med.quantity:
            messages.error(request, f'Only {med.quantity} units in stock.')
            return redirect('medicine_list')
        StockMovement.objects.create(
            medicine=med, movement_type=move_type, quantity=qty,
            unit_price=request.POST.get('unit_price',0),
            reason=request.POST.get('reason',''),
            performed_by=request.user,
        )
        messages.success(request, 'Stock updated successfully.')
    return redirect('medicine_list')

@login_required
def stock_history(request):
    movements = StockMovement.objects.select_related('medicine','performed_by').order_by('-date')[:100]
    return render(request,'pharmacy/stock_history.html',{'movements':movements})

@login_required
def prescription_list(request):
    rxs = Prescription.objects.select_related('patient','doctor').order_by('-date')
    return render(request,'pharmacy/prescription_list.html',{'prescriptions':rxs})

@login_required
def prescription_create(request, patient_pk=None):
    patients = Patient.objects.filter(is_active=True)
    meds     = Medicine.objects.filter(is_active=True, quantity__gt=0)
    patient  = get_object_or_404(Patient, pk=patient_pk) if patient_pk else None
    if request.method == 'POST':
        pat = get_object_or_404(Patient, pk=request.POST['patient'])
        rx  = Prescription.objects.create(patient=pat, doctor=request.user,
                                          notes=request.POST.get('notes',''))
        med_ids   = request.POST.getlist('medicine')
        quantities= request.POST.getlist('quantity')
        dosages   = request.POST.getlist('dosage')
        durations = request.POST.getlist('duration')
        for i, mid in enumerate(med_ids):
            if mid:
                PrescriptionItem.objects.create(
                    prescription=rx, medicine_id=mid,
                    quantity=int(quantities[i]) if i<len(quantities) else 1,
                    dosage=dosages[i]   if i<len(dosages)   else '',
                    duration=durations[i] if i<len(durations) else '',
                )
        messages.success(request,'Prescription created.')
        return redirect('prescription_list')
    return render(request,'pharmacy/prescription_form.html',
                  {'patients':patients,'meds':meds,'patient':patient})

@login_required
def dispense_prescription(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    if not rx.is_dispensed:
        for item in rx.items.all():
            if item.medicine.quantity < item.quantity:
                messages.error(request,f'Insufficient stock for {item.medicine.name}.')
                return redirect('prescription_list')
        for item in rx.items.all():
            StockMovement.objects.create(
                medicine=item.medicine, movement_type='out', quantity=item.quantity,
                performed_by=request.user, reason=f'Prescription #{rx.pk}'
            )
        rx.is_dispensed = True
        rx.dispensed_at = timezone.now()
        rx.save()
        messages.success(request,'Prescription dispensed successfully.')
    return redirect('prescription_list')
