from django.contrib import admin
from .models import Medicine, MedicineCategory, StockMovement, Prescription, PrescriptionItem
admin.site.register(Medicine)
admin.site.register(MedicineCategory)
admin.site.register(StockMovement)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)
