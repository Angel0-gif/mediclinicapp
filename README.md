# MediCare – Clinic Management System

A full Django web application for managing daily clinic operations.

## Modules
- **Dashboard** – Real-time overview: patients, appointments, cash flow, stock alerts
- **Patients** – Registration, medical records, patient login portal
- **Appointments** – Scheduling, status tracking (scheduled → completed)
- **Pharmacy** – Medicine inventory, stock movements, prescriptions, dispensing
- **Finance** – Income/expense transactions, bills & payment collection
- **Staff & HR** – Staff directory, daily attendance, monthly payroll
- **Reports** – Financial report, pharmacy report, patient statistics

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database + create admin account
python setup.py

# 3. Run the server
python manage.py runserver

# 4. Open browser
# http://127.0.0.1:8000/
# Login: admin / admin123
```

## User Roles
| Role | Access |
|------|--------|
| Admin | Full access to all modules including HR & Reports |
| Doctor | Clinical modules (patients, appointments, prescriptions) |
| Nurse | Patients, appointments |
| Cashier | Finance, billing |
| Receptionist | Patients, appointments |
| Patient | Personal portal (appointments, prescriptions) |

## Technology
- **Backend**: Django 4.2 (Python)
- **Database**: SQLite (easily switchable to PostgreSQL)
- **Frontend**: Pure HTML/CSS/JS (no extra frameworks needed)
- **Currency**: XAF (Central African Franc)
- **Timezone**: Africa/Douala

## Production Notes
- Change `SECRET_KEY` in `clinic/settings.py`
- Set `DEBUG = False`
- Configure a proper database (PostgreSQL recommended)
- Set up proper static file serving (WhiteNoise or Nginx)

## Troubleshooting

### "no such table" error on setup.py
Delete the old database file and re-run setup:
```bash
# Windows
del db.sqlite3
python setup.py

# Linux/Mac
rm -f db.sqlite3
python setup.py
```

### "No module named 'apps'" error
Make sure you're running commands from inside the `mediclinic/` folder (where `manage.py` is).
