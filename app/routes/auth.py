import re
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, VALID_ROLES

auth = Blueprint('auth', __name__)

# ── Security Constants ─────────────────────────────────────────────────────
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES    = 15
MIN_PASSWORD_LEN   = 10


def _password_strength_errors(password):
    errors = []
    if len(password) < MIN_PASSWORD_LEN:
        errors.append(f'At least {MIN_PASSWORD_LEN} characters.')
    if not re.search(r'[A-Z]', password):
        errors.append('At least one uppercase letter (A-Z).')
    if not re.search(r'[a-z]', password):
        errors.append('At least one lowercase letter (a-z).')
    if not re.search(r'\d', password):
        errors.append('At least one number (0-9).')
    if not re.search(r'[!@#$%^&*()\-_=+\[\]{};\':"\\|,.<>/?`~]', password):
        errors.append('At least one special character e.g. !@#$%.')
    return errors


def _is_locked(user):
    return bool(user.locked_until and user.locked_until > datetime.utcnow())


def _reset_attempts(user):
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()


def _record_failed(user):
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
    db.session.commit()


# ── Role Selection (entry page) ────────────────────────────────────────────
@auth.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return redirect(url_for('auth.role_select'))


@auth.route('/select-role')
def role_select():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return render_template('auth/role_select.html')


# ── Register ───────────────────────────────────────────────────────────────
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    role = (request.form.get('role') or request.args.get('role', 'patient')).lower()
    if role not in VALID_ROLES:
        flash('Invalid role. Please choose again.', 'danger')
        return redirect(url_for('auth.role_select'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not all([name, email, password]):
            flash('All fields are required.', 'danger')
        elif len(name) < 2:
            flash('Name must be at least 2 characters.', 'danger')
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Please enter a valid email address.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            pw_errors = _password_strength_errors(password)
            if pw_errors:
                for err in pw_errors:
                    flash(f'Password requires: {err}', 'danger')
            elif User.query.filter_by(email=email).first():
                flash('An account with this email already exists.', 'danger')
            else:
                user = User(name=name, email=email, role=role)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash(f'Welcome to TrackLife, {name}! Your {role.capitalize()} account is ready.', 'success')
                return redirect(url_for('dashboard.home'))

    return render_template('auth/register.html', role=role)


# ── Login ──────────────────────────────────────────────────────────────────
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()

        if not user:
            flash('Invalid email or password.', 'danger')
        elif _is_locked(user):
            mins = int((user.locked_until - datetime.utcnow()).total_seconds() // 60) + 1
            flash(f'Account locked. Try again in {mins} minute(s).', 'danger')
        elif user.check_password(password):
            _reset_attempts(user)
            login_user(user, remember=True)
            return redirect(url_for('dashboard.home'))
        else:
            _record_failed(user)
            left = MAX_LOGIN_ATTEMPTS - (user.failed_login_attempts or 0)
            if left > 0:
                flash(f'Invalid email or password. {left} attempt(s) left before lockout.', 'danger')
            else:
                flash(f'Account locked for {LOCKOUT_MINUTES} minutes.', 'danger')

    return render_template('auth/login.html')


# ── Logout ─────────────────────────────────────────────────────────────────
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
