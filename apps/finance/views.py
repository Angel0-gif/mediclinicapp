from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date, timedelta
from .models import Transaction, TransactionCategory, Bill, BillItem
from apps.patients.models import Patient

@login_required
def finance_dashboard(request):
    today = date.today()
    ms    = today.replace(day=1)
    S = lambda qs: qs.aggregate(t=Sum('amount'))['t'] or 0
    ti = S(Transaction.objects.filter(date=today,  transaction_type='income'))
    te = S(Transaction.objects.filter(date=today,  transaction_type='expense'))
    mi = S(Transaction.objects.filter(date__gte=ms,transaction_type='income'))
    me = S(Transaction.objects.filter(date__gte=ms,transaction_type='expense'))
    chart = []
    for i in range(29,-1,-1):
        d = today - timedelta(days=i)
        chart.append({'day':d.strftime('%d/%m'),
            'income': float(S(Transaction.objects.filter(date=d,transaction_type='income'))),
            'expense':float(S(Transaction.objects.filter(date=d,transaction_type='expense')))})
    return render(request,'finance/dashboard.html',{
        'today_in':ti,'today_out':te,'today_net':ti-te,
        'month_in':mi,'month_out':me,'month_net':mi-me,
        'recent': Transaction.objects.select_related('patient','category').order_by('-created_at')[:15],
        'chart_data': chart,
        'pending_bills': Bill.objects.filter(status__in=['pending','partial']).select_related('patient'),
    })

@login_required
def transaction_list(request):
    start = request.GET.get('start', str(date.today().replace(day=1)))
    end   = request.GET.get('end',   str(date.today()))
    ttype = request.GET.get('type','')
    txns  = Transaction.objects.select_related('patient','category').filter(date__gte=start,date__lte=end)
    if ttype: txns = txns.filter(transaction_type=ttype)
    S = lambda qs: qs.aggregate(t=Sum('amount'))['t'] or 0
    return render(request,'finance/transaction_list.html',{
        'txns': txns.order_by('-date','-created_at'),
        'total_in':  S(txns.filter(transaction_type='income')),
        'total_out': S(txns.filter(transaction_type='expense')),
        'start':start,'end':end,'ttype':ttype,
        'categories': TransactionCategory.objects.all(),
        'patients':   Patient.objects.filter(is_active=True),
    })

@login_required
def transaction_create(request):
    if request.method == 'POST':
        cat_id = request.POST.get('category')
        pat_id = request.POST.get('patient')
        Transaction.objects.create(
            transaction_type=request.POST['transaction_type'],
            category_id=cat_id or None, patient_id=pat_id or None,
            amount=request.POST['amount'],
            payment_method=request.POST.get('payment_method','cash'),
            description=request.POST.get('description',''),
            reference=request.POST.get('reference',''),
            date=request.POST.get('date', str(date.today())),
            recorded_by=request.user,
        )
        messages.success(request,'Transaction recorded.')
        return redirect('transaction_list')
    return render(request,'finance/transaction_form.html',{
        'categories': TransactionCategory.objects.all(),
        'patients':   Patient.objects.filter(is_active=True),
        'today': str(date.today()),
    })

@login_required
def bill_list(request):
    bills = Bill.objects.select_related('patient').order_by('-created_at')
    return render(request,'finance/bill_list.html',{'bills':bills})

@login_required
def bill_create(request, patient_pk=None):
    patient  = get_object_or_404(Patient, pk=patient_pk) if patient_pk else None
    patients = Patient.objects.filter(is_active=True)
    if request.method == 'POST':
        pat  = get_object_or_404(Patient, pk=request.POST['patient'])
        bill = Bill.objects.create(patient=pat,notes=request.POST.get('notes',''),created_by=request.user)
        descs  = request.POST.getlist('description')
        qtys   = request.POST.getlist('quantity')
        prices = request.POST.getlist('unit_price')
        total  = 0
        for i, desc in enumerate(descs):
            if desc:
                qty   = int(qtys[i])   if i<len(qtys)   else 1
                price = float(prices[i]) if i<len(prices) else 0
                BillItem.objects.create(bill=bill,description=desc,quantity=qty,unit_price=price)
                total += qty*price
        bill.total_amount = total
        bill.save()
        messages.success(request,f'Bill #{bill.pk} created.')
        return redirect('bill_detail',pk=bill.pk)
    return render(request,'finance/bill_form.html',{'patients':patients,'patient':patient})

@login_required
def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        paid = float(request.POST.get('paid_amount',0))
        bill.paid_amount += paid
        bill.status = 'paid' if bill.paid_amount >= bill.total_amount else ('partial' if bill.paid_amount>0 else 'pending')
        bill.save()
        Transaction.objects.create(
            transaction_type='income', patient=bill.patient, amount=paid,
            payment_method=request.POST.get('payment_method','cash'),
            description=f'Payment for Bill #{bill.pk}',
            date=date.today(), recorded_by=request.user,
        )
        messages.success(request,f'Payment of {paid:,.0f} XAF recorded.')
        return redirect('bill_detail',pk=pk)
    return render(request,'finance/bill_detail.html',{'bill':bill})
