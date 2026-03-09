import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import MedicalRecord, FamilyMember, Reminder
from datetime import datetime, date

records = Blueprint('records', __name__)

RECORD_TYPES = ['Prescription', 'Lab Test', 'Doctor Visit', 'Scan / Imaging', 'Vaccination', 'Other']
CATEGORIES = ['General', 'ENT', 'Cardiology', 'Orthopedics', 'Dermatology',
              'Neurology', 'Diabetes', 'Ophthalmology', 'Dental', 'Gynecology', 'Pediatrics']


def allowed_file(filename):
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_file(file):
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, unique_name))
    return unique_name


# ── Records List ──────────────────────────────────────────────────────────────
@records.route('/records')
@login_required
def list_records():
    search = request.args.get('q', '').strip()
    rtype = request.args.get('type', '')
    category = request.args.get('category', '')

    query = MedicalRecord.query.filter_by(user_id=current_user.id)
    if search:
        query = query.filter(
            (MedicalRecord.title.ilike(f'%{search}%')) |
            (MedicalRecord.doctor_name.ilike(f'%{search}%')) |
            (MedicalRecord.hospital.ilike(f'%{search}%'))
        )
    if rtype:
        query = query.filter_by(record_type=rtype)
    if category:
        query = query.filter_by(category=category)

    all_records = query.order_by(MedicalRecord.visit_date.desc()).all()
    return render_template('records/list.html', records=all_records,
                           record_types=RECORD_TYPES, categories=CATEGORIES,
                           search=search, rtype=rtype, category=category)


# ── Add Record ────────────────────────────────────────────────────────────────
@records.route('/records/add', methods=['GET', 'POST'])
@login_required
def add_record():
    family = FamilyMember.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        record_type = request.form.get('record_type', '')
        category = request.form.get('category', 'General')
        doctor_name = request.form.get('doctor_name', '').strip()
        hospital = request.form.get('hospital', '').strip()
        notes = request.form.get('notes', '').strip()
        visit_date_str = request.form.get('visit_date', '')
        family_member_id = request.form.get('family_member_id') or None

        if not all([title, record_type, visit_date_str]):
            flash('Title, type, and visit date are required.', 'danger')
            return render_template('records/add.html', record_types=RECORD_TYPES,
                                   categories=CATEGORIES, family=family)

        visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()

        filename = None
        file = request.files.get('document')
        if file and file.filename and allowed_file(file.filename):
            filename = save_file(file)

        record = MedicalRecord(
            title=title, record_type=record_type, category=category,
            doctor_name=doctor_name, hospital=hospital, notes=notes,
            filename=filename, visit_date=visit_date,
            user_id=current_user.id,
            family_member_id=int(family_member_id) if family_member_id else None
        )
        db.session.add(record)
        db.session.commit()
        flash('Record added successfully!', 'success')
        return redirect(url_for('records.list_records'))

    return render_template('records/add.html', record_types=RECORD_TYPES,
                           categories=CATEGORIES, family=family)


# ── View Record ───────────────────────────────────────────────────────────────
@records.route('/records/<int:record_id>')
@login_required
def view_record(record_id):
    record = MedicalRecord.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
    return render_template('records/view.html', record=record)


# ── Delete Record ─────────────────────────────────────────────────────────────
@records.route('/records/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    record = MedicalRecord.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
    if record.filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], record.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted.', 'info')
    return redirect(url_for('records.list_records'))


# ── Serve Uploaded Files ──────────────────────────────────────────────────────
@records.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# ── Family Members ────────────────────────────────────────────────────────────
@records.route('/family', methods=['GET', 'POST'])
@login_required
def family():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        relation = request.form.get('relation', '').strip()
        dob_str = request.form.get('dob', '')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        if name and relation:
            member = FamilyMember(name=name, relation=relation, dob=dob, user_id=current_user.id)
            db.session.add(member)
            db.session.commit()
            flash(f'{name} added to your family.', 'success')
        return redirect(url_for('records.family'))

    members = FamilyMember.query.filter_by(user_id=current_user.id).all()
    return render_template('records/family.html', members=members)


# ── Reminders ─────────────────────────────────────────────────────────────────
@records.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminders():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        due_date_str = request.form.get('due_date', '')
        if title and due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            reminder = Reminder(title=title, due_date=due_date, user_id=current_user.id)
            db.session.add(reminder)
            db.session.commit()
            flash('Reminder set!', 'success')
        return redirect(url_for('records.reminders'))

    all_reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.due_date).all()
    today = date.today()
    return render_template('records/reminders.html', reminders=all_reminders, today=today)


@records.route('/reminders/<int:reminder_id>/done', methods=['POST'])
@login_required
def mark_done(reminder_id):
    reminder = Reminder.query.filter_by(id=reminder_id, user_id=current_user.id).first_or_404()
    reminder.is_done = True
    db.session.commit()
    return redirect(url_for('records.reminders'))
