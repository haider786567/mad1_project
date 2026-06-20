from flask import Blueprint, render_template, redirect, request, url_for ,flash 
from werkzeug.security import generate_password_hash, check_password_hash
from models import User,db
from functools import wraps
from flask_login import login_user, logout_user, current_user, login_required  




auth_bp = Blueprint('auth', __name__)




def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function




@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff.dashboard'))
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('auth/login.html')
    
    
    

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if not name or not email or not password or role not in ('user', 'staff'):
            flash('Please complete all fields and select a valid role.', 'danger')
            return render_template('auth/register.html')

        if role == 'staff':
            status = 'pending'
        else:
            status = 'approved'
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('auth.login'))
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role,
            status=status
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
