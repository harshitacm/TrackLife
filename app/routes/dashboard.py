from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import MedicalRecord, Reminder, FamilyMember
from datetime import date, timedelta
from collections import Counter

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard')
@login_required
def home():
    records = MedicalRecord.query.filter_by(user_id=current_user.id).order_by(
        MedicalRecord.visit_date.desc()).all()

    today = date.today()
    upcoming = Reminder.query.filter(
        Reminder.user_id == current_user.id,
        Reminder.is_done == False,
        Reminder.due_date >= today,
        Reminder.due_date <= today + timedelta(days=30)
    ).order_by(Reminder.due_date).limit(5).all()

    recent = records[:5]
    total = len(records)

    category_counts = Counter(r.category for r in records if r.category)
    type_counts = Counter(r.record_type for r in records)
    family_count = FamilyMember.query.filter_by(user_id=current_user.id).count()

    return render_template('dashboard/home.html',
                           recent=recent,
                           upcoming=upcoming,
                           total=total,
                           family_count=family_count,
                           category_counts=dict(category_counts),
                           type_counts=dict(type_counts))
