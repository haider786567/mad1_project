from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from controller.auth import admin_required , login_required
from models import Trek


staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/pending')
@login_required
def pending_approval():
    """View pending approval treks."""
    if current_user.role != 'staff':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user.dashboard'))
    pending_treks = Trek.query.filter_by(status='Pending').all()
    return render_template('staff/pending_approval.html', treks=pending_treks)
@staff_bp.route('/dashboard')
@login_required
def dashboard():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    trek_data = []
    for trek in assigned_treks:
        participants_count = trek.participants.count()
        trek_data.append({
            'trek': trek,
            'participants_count': participants_count
        })
    return render_template('staff/dashboard.html', trek_data=trek_data)

