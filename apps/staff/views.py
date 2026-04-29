from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import StaffProfile, Attendance, PayrollRecord

@login_required
def staff_list(request):
    staff = StaffProfile.objects.select_related('user').filter(is_active=True)
    return render(request,'staff/list.html',{'staff':staff})

@login_required
def staff_detail(request, pk):
    member = get_object_or_404(StaffProfile, pk=pk)
    return render(request,'staff/detail.html',{
        'member': member,
        'attendance': member.attendance.order_by('-date')[:30],
        'payroll':    member.payroll.order_by('-month')[:12],
    })

@login_required
def attendance_today(request):
    today = date.today()
    staff = StaffProfile.objects.filter(is_active=True).select_related('user')
    attendance_map = {a.staff_id: a for a in Attendance.objects.filter(date=today)}
    if request.method == 'POST':
        for member in staff:
            status    = request.POST.get(f'status_{member.pk}','absent')
            check_in  = request.POST.get(f'checkin_{member.pk}','') or None
            check_out = request.POST.get(f'checkout_{member.pk}','') or None
            Attendance.objects.update_or_create(
                staff=member, date=today,
                defaults={'status':status,'check_in':check_in,'check_out':check_out}
            )
        messages.success(request,'Attendance saved.')
        return redirect('attendance_today')
    return render(request,'staff/attendance.html',{
        'staff':staff,'attendance_map':attendance_map,'today':today})

@login_required
def payroll_list(request):
    month_str = request.GET.get('month', date.today().strftime('%Y-%m'))
    try:
        month = date.fromisoformat(month_str+'-01')
    except Exception:
        month = date.today().replace(day=1)
    records = PayrollRecord.objects.filter(month=month).select_related('staff__user')
    staff_without = StaffProfile.objects.filter(is_active=True).exclude(
        pk__in=records.values_list('staff__pk',flat=True))
    return render(request,'staff/payroll.html',{
        'records':records,'month':month,
        'month_str':month.strftime('%Y-%m'),'staff_without':staff_without,
    })

@login_required
def generate_payroll(request):
    if request.method == 'POST':
        month_str = request.POST.get('month')
        month     = date.fromisoformat(month_str+'-01')
        created   = 0
        for member in StaffProfile.objects.filter(is_active=True):
            _, flag = PayrollRecord.objects.get_or_create(
                staff=member, month=month,
                defaults={'base_salary':member.salary,'bonus':0,'deductions':0}
            )
            if flag: created += 1
        messages.success(request,f'Payroll generated for {created} staff.')
    return redirect('payroll_list')

@login_required
def mark_payroll_paid(request, pk):
    record = get_object_or_404(PayrollRecord, pk=pk)
    record.is_paid   = True
    record.paid_date = date.today()
    record.save()
    from apps.finance.models import Transaction
    Transaction.objects.create(
        transaction_type='expense', amount=record.net_pay,
        description=f'Salary – {record.staff.user.get_full_name()} – {record.month.strftime("%B %Y")}',
        date=date.today(), recorded_by=request.user,
    )
    messages.success(request,'Marked as paid and expense recorded.')
    return redirect('payroll_list')
