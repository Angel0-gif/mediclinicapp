from django.db import models
from django.contrib.auth.models import User
from apps.patients.models import Patient

class Appointment(models.Model):
    STATUS_CHOICES = [('scheduled','Scheduled'),('confirmed','Confirmed'),
        ('in_progress','In Progress'),('completed','Completed'),
        ('cancelled','Cancelled'),('no_show','No Show')]
    TYPE_CHOICES = [('consultation','Consultation'),('follow_up','Follow-up'),
        ('emergency','Emergency'),('lab_test','Lab Test'),
        ('vaccination','Vaccination'),('procedure','Procedure')]
    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor           = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date             = models.DateField()
    time             = models.TimeField()
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='consultation')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reason           = models.TextField(blank=True)
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['date','time']
    def __str__(self): return f"{self.patient} – {self.date} {self.time}"
