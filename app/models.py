from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import bcrypt


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


VALID_ROLES = ('patient', 'nurse', 'doctor')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    records = db.relationship('MedicalRecord', backref='owner', lazy=True)
    family_members = db.relationship('FamilyMember', backref='primary_user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )


class FamilyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    relation = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    records = db.relationship('MedicalRecord', backref='family_member', lazy=True)


class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    doctor_name = db.Column(db.String(100), nullable=True)
    hospital = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(200), nullable=True)
    visit_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    family_member_id = db.Column(db.Integer, db.ForeignKey('family_member.id'), nullable=True)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
