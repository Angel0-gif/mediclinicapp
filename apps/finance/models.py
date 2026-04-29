from django.db import models
from django.contrib.auth.models import User
from apps.patients.models import Patient

class TransactionCategory(models.Model):
    name             = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=10, choices=[('income','Income'),('expense','Expense')])
    def __str__(self): return f"{self.name} ({self.transaction_type})"

class Transaction(models.Model):
    TYPE_CHOICES    = [('income','Income'),('expense','Expense')]
    PAYMENT_CHOICES = [('cash','Cash'),('mobile','Mobile Money'),('card','Card'),
                       ('insurance','Insurance'),('other','Other')]
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category         = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    patient          = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    amount           = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method   = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    description      = models.TextField(blank=True)
    reference        = models.CharField(max_length=100, blank=True)
    date             = models.DateField()
    recorded_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-date','-created_at']
    def __str__(self): return f"{self.transaction_type.upper()} {self.amount} – {self.date}"

class Bill(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('partial','Partial'),('paid','Paid'),('cancelled','Cancelled')]
    patient      = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    date         = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes        = models.TextField(blank=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    @property
    def balance(self): return self.total_amount - self.paid_amount
    def __str__(self): return f"Bill #{self.pk} – {self.patient} – {self.status}"

class BillItem(models.Model):
    bill        = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity    = models.IntegerField(default=1)
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self): return self.quantity * self.unit_price
