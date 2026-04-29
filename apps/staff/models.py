from django.db import models
from django.contrib.auth.models import User

class StaffProfile(models.Model):
    DEPT_CHOICES = [('medical','Medical'),('nursing','Nursing'),('pharmacy','Pharmacy'),
                    ('admin','Administration'),('finance','Finance'),('lab','Laboratory')]
    EMP_CHOICES  = [('full_time','Full Time'),('part_time','Part Time'),('contract','Contract')]
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    department      = models.CharField(max_length=30, choices=DEPT_CHOICES)
    employment_type = models.CharField(max_length=20, choices=EMP_CHOICES, default='full_time')
    hire_date       = models.DateField()
    salary          = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qualifications  = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    is_active       = models.BooleanField(default=True)
    def __str__(self): return f"{self.user.get_full_name()} – {self.department}"

class Attendance(models.Model):
    STATUS_CHOICES = [('present','Present'),('absent','Absent'),('leave','Leave'),('half_day','Half Day')]
    staff     = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='attendance')
    date      = models.DateField()
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    check_in  = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    notes     = models.CharField(max_length=200, blank=True)
    class Meta: unique_together = ['staff','date']
    def __str__(self): return f"{self.staff} – {self.date} – {self.status}"

class PayrollRecord(models.Model):
    staff       = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='payroll')
    month       = models.DateField()
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    bonus       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid     = models.BooleanField(default=False)
    paid_date   = models.DateField(null=True, blank=True)
    notes       = models.TextField(blank=True)
    class Meta: unique_together = ['staff','month']
    def save(self, *args, **kwargs):
        self.net_pay = self.base_salary + self.bonus - self.deductions
        super().save(*args, **kwargs)
