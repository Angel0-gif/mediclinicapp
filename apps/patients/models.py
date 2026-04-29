from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    GENDER_CHOICES = [('M','Male'),('F','Female'),('O','Other')]
    BLOOD_CHOICES  = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
                      ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]
    user                    = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name              = models.CharField(max_length=100)
    last_name               = models.CharField(max_length=100)
    date_of_birth           = models.DateField()
    gender                  = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group             = models.CharField(max_length=3, choices=BLOOD_CHOICES, blank=True)
    phone                   = models.CharField(max_length=20)
    email                   = models.EmailField(blank=True)
    address                 = models.TextField(blank=True)
    emergency_contact_name  = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    allergies               = models.TextField(blank=True)
    chronic_conditions      = models.TextField(blank=True)
    notes                   = models.TextField(blank=True)
    registered_at           = models.DateTimeField(auto_now_add=True)
    is_active               = models.BooleanField(default=True)

    class Meta: ordering = ['-registered_at']

    def __str__(self): return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self): return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        t = date.today()
        return t.year - self.date_of_birth.year - ((t.month,t.day) < (self.date_of_birth.month,self.date_of_birth.day))


class MedicalRecord(models.Model):
    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='records')
    doctor           = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date             = models.DateField(auto_now_add=True)
    chief_complaint  = models.TextField()
    diagnosis        = models.TextField()
    treatment        = models.TextField()
    notes            = models.TextField(blank=True)
    follow_up_date   = models.DateField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-created_at']
    def __str__(self): return f"{self.patient} - {self.date}"
