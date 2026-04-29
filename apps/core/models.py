from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin','Administrator'),('doctor','Doctor'),('nurse','Nurse'),
        ('cashier','Cashier'),('receptionist','Receptionist'),('patient','Patient'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

    def is_admin(self): return self.role == 'admin'
    def is_patient(self): return self.role == 'patient'
