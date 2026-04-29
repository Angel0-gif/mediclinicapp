"""
Run this script once after installing requirements.
Usage: python setup.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command

print("Creating migrations...")
call_command('makemigrations', 'core',         verbosity=0)
call_command('makemigrations', 'patients',     verbosity=0)
call_command('makemigrations', 'appointments', verbosity=0)
call_command('makemigrations', 'pharmacy',     verbosity=0)
call_command('makemigrations', 'finance',      verbosity=0)
call_command('makemigrations', 'staff',        verbosity=0)
call_command('makemigrations', 'reports',      verbosity=0)
print("Applying migrations...")
call_command('migrate', verbosity=0)
print("✓ Database ready")

from django.contrib.auth.models import User
from apps.core.models import UserProfile
from apps.pharmacy.models import MedicineCategory
from apps.finance.models import TransactionCategory

# Admin account
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        'admin', 'admin@clinic.cm', 'admin123',
        first_name='Admin', last_name='Clinic'
    )
    UserProfile.objects.filter(user=admin).update(role='admin')
    print("✓ Admin created  →  username=admin  password=admin123")
else:
    UserProfile.objects.filter(user__username='admin').update(role='admin')
    print("✓ Admin account already exists")

# Medicine categories
cats = ['Antibiotics','Analgesics','Antihypertensives','Antidiabetics',
        'Vitamins & Supplements','Antimalarials','Antiparasitics','Other']
for name in cats:
    MedicineCategory.objects.get_or_create(name=name)
print(f"✓ {len(cats)} medicine categories ready")

# Transaction categories
tcats = [
    ('Consultation Fees','income'), ('Laboratory Fees','income'),
    ('Pharmacy Sales','income'),    ('Vaccination','income'),
    ('Other Income','income'),      ('Medicine Purchase','expense'),
    ('Salaries','expense'),         ('Utilities','expense'),
    ('Equipment','expense'),        ('Other Expense','expense'),
]
for name, ttype in tcats:
    TransactionCategory.objects.get_or_create(name=name, transaction_type=ttype)
print(f"✓ {len(tcats)} transaction categories ready")

print("\n✅  Setup complete!")
print("   Run:   python manage.py runserver")
print("   Open:  http://127.0.0.1:8000/")
print("   Login: admin / admin123")
