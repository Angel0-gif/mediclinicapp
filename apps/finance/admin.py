from django.contrib import admin
from .models import Transaction, TransactionCategory, Bill, BillItem
admin.site.register(Transaction)
admin.site.register(TransactionCategory)
admin.site.register(Bill)
admin.site.register(BillItem)
