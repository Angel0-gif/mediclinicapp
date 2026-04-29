from django.db import models
from django.contrib.auth.models import User
from apps.patients.models import Patient

class MedicineCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Medicine(models.Model):
    UNIT_CHOICES = [('tablet','Tablet'),('capsule','Capsule'),('syrup','Syrup'),
                    ('injection','Injection'),('cream','Cream'),('drops','Drops'),('other','Other')]
    name           = models.CharField(max_length=200)
    generic_name   = models.CharField(max_length=200, blank=True)
    category       = models.ForeignKey(MedicineCategory, on_delete=models.SET_NULL, null=True, blank=True)
    unit           = models.CharField(max_length=20, choices=UNIT_CHOICES, default='tablet')
    quantity       = models.IntegerField(default=0)
    min_stock      = models.IntegerField(default=10)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiry_date    = models.DateField(null=True, blank=True)
    manufacturer   = models.CharField(max_length=200, blank=True)
    description    = models.TextField(blank=True)
    is_active      = models.BooleanField(default=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta: ordering = ['name']
    def __str__(self): return self.name

    @property
    def is_low_stock(self): return self.quantity <= self.min_stock

    @property
    def is_expired(self):
        from datetime import date
        return self.expiry_date and self.expiry_date < date.today()

class StockMovement(models.Model):
    MOVE_CHOICES = [('in','Stock In'),('out','Stock Out'),('adjustment','Adjustment')]
    medicine      = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVE_CHOICES)
    quantity      = models.IntegerField()
    unit_price    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason        = models.CharField(max_length=200, blank=True)
    performed_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date          = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.medicine} {self.movement_type} {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        med = self.medicine
        if self.movement_type == 'in':
            med.quantity += self.quantity
        elif self.movement_type == 'out':
            med.quantity = max(0, med.quantity - self.quantity)
        elif self.movement_type == 'adjustment':
            med.quantity = self.quantity
        med.save(update_fields=['quantity'])

class Prescription(models.Model):
    patient      = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date         = models.DateField(auto_now_add=True)
    notes        = models.TextField(blank=True)
    is_dispensed = models.BooleanField(default=False)
    dispensed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self): return f"Rx#{self.pk} – {self.patient} – {self.date}"

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine     = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity     = models.IntegerField()
    dosage       = models.CharField(max_length=200)
    duration     = models.CharField(max_length=100)
    def __str__(self): return f"{self.medicine} x{self.quantity}"
