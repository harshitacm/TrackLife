# TrackLife
Overview TrackLife is a Flask web application for managing health records securely. It supports three distinct user roles — Patient, Nurse, and Doctor — each with a tailored feature set. Authentication is hardened with brute-force lockout, strong password enforcement, and role validation on every route.
# 🏥 TrackLife

A Flask-based health records platform with role-based access for **Patients**, **Nurses**, and **Doctors**.

---

## Project Structure

```
tracklife/
├── run.py
├── config.py
├── requirements.txt
└── app/
    ├── __init__.py
    ├── models.py
    ├── routes/
    │   ├── auth.py          # login, register, role select, logout
    │   ├── dashboard.py     # role-aware dashboard
    │   ├── records.py       # nurse/doctor: records, family, reminders
    │   └── patient.py       # patient: health log, medications, appointments
    ├── templates/
    │   ├── base.html        # navbar with role-aware links
    │   ├── auth/            # login.html, register.html, role_select.html
    │   ├── dashboard/       # home.html (branches by role)
    │   ├── records/         # list, add, view, family, reminders
    │   └── patient/         # health_log, medications, appointments
    └── static/
        ├── css/style.css
        └── js/main.js
```

---

## Roles & Features

| Feature | Nurse / Doctor | Patient |
|---|---|---|
| Dashboard | Records overview + reminders | Health entries + appointments |
| Nav Item 1 | Records | My Health |
| Nav Item 2 | Family Members | Medications |
| Nav Item 3 | Reminders | Appointments |
| Vitals Tracking | ✗ | ✓ Weight, BP |
| Mood / Energy | ✗ | ✓ Per day |
| Medication Mgmt | ✗ | ✓ |
| Appointment Booking | ✗ | ✓ |
| Clinical Records | ✓ | ✗ |
| Family Member Mgmt | ✓ | ✗ |

---

## Database Models

### Shared

| Model | Key Fields | Used By |
|---|---|---|
| `User` | id, name, email, password_hash, role, failed_login_attempts, locked_until | All |
| `MedicalRecord` | title, record_type, category, doctor_name, hospital, notes, filename, visit_date | Nurse, Doctor |
| `FamilyMember` | name, relation, dob, user_id | Nurse, Doctor |
| `Reminder` | title, due_date, is_done, user_id | Nurse, Doctor |

### Patient-Only

| Model | Key Fields |
|---|---|
| `HealthLog` | log_date, mood, energy (1–5), symptoms, notes, weight_kg, bp_systolic, bp_diastolic |
| `Medication` | name, dosage, frequency, start_date, end_date, prescribed_by, notes, is_active |
| `Appointment` | title, doctor_name, hospital, appt_date, appt_time, notes, is_done |

---

## Authentication & Security

| Feature | Detail |
|---|---|
| Role Selection | Landing page at `/` — choose role before registering |
| Password Policy | Min 10 chars, uppercase, lowercase, number, special character |
| Brute-Force Lockout | Account locked 15 min after 5 failed login attempts |
| Attempt Counter | Remaining attempts shown in flash before lockout |
| Generic Errors | Always returns `Invalid email or password` — never reveals if email exists |
| Role Guard | `patient_only()` on every patient route — non-patients get HTTP 403 |
| Password Hashing | bcrypt with salt |
| Session | flask-login with `remember=True` |

---

## Setup

```bash
# 1. Clone and create virtual environment
git clone <repo-url>
cd tracklife
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Set SECRET_KEY in .env

# 4. Run
python run.py
# App runs at http://127.0.0.1:5000
```

> **After pulling updates with new models:**
> ```bash
> flask db migrate -m "add patient models"
> flask db upgrade
> # or for dev: rm app/tracklife.db && python run.py
> ```

---

## Routes

### Auth

| Method | Route | Description |
|---|---|---|
| GET | `/` | Redirects to `/select-role` |
| GET | `/select-role` | Role selection landing page |
| GET / POST | `/register?role=<role>` | Registration form |
| GET / POST | `/login` | Login with lockout enforcement |
| GET | `/logout` | Clears session |

### Nurse / Doctor

| Method | Route | Description |
|---|---|---|
| GET | `/dashboard` | Clinical dashboard |
| GET | `/records` | List records with search & filter |
| GET / POST | `/records/add` | Add a new medical record |
| GET | `/records/<id>` | View record detail |
| POST | `/records/<id>/delete` | Delete record |
| GET / POST | `/family` | Manage family members |
| GET / POST | `/reminders` | Set and view reminders |
| POST | `/reminders/<id>/done` | Mark reminder as done |

### Patient

| Method | Route | Description |
|---|---|---|
| GET / POST | `/my-health` | Daily health log |
| POST | `/my-health/<id>/delete` | Delete a log entry |
| GET / POST | `/medications` | View and add medications |
| POST | `/medications/<id>/stop` | Mark medication as stopped |
| POST | `/medications/<id>/delete` | Remove medication |
| GET / POST | `/appointments` | Book and view appointments |
| POST | `/appointments/<id>/done` | Mark appointment as done |
| POST | `/appointments/<id>/delete` | Remove appointment |

---

## Requirements

| Package | Purpose |
|---|---|
| `Flask` | Web framework |
| `Flask-SQLAlchemy` | ORM / database |
| `Flask-Login` | Session management |
| `flask-bcrypt` | Password hashing |
| `python-dotenv` | Environment variables |

---

## Notes

- Upload folder defaults to `app/static/uploads/` — change `UPLOAD_FOLDER` in `config.py` for production
- File uploads: PDF, JPG, PNG — 16 MB max
- Nurse and Doctor roles share identical access; extend via the `role` field on `User` if needed
- For production: use PostgreSQL and set a strong `SECRET_KEY`
