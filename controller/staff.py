from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from controller.auth import  login_required
from models import Booking, Trek, User,db


staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/pending')
@login_required
def pending_approval():
    """View pending approval treks."""
    if current_user.role != 'staff':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))
    if current_user.role == 'staff' and current_user.status == 'approved':
        print(current_user)
        print(User)
        flash('You are already approved.', 'info')
        return redirect(url_for('staff.dashboard'))
    return render_template('staff/pending_approval.html')
@staff_bp.route('/dashboard')
@login_required
def dashboard():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    trek_data = []
    for trek in assigned_treks:
        participants_count = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.status.ilike('booked')
        ).count()
        trek_data.append({
            'trek': trek,
            'participants_count': participants_count
        })
    return render_template('staff/dashboard.html', trek_data=trek_data)

@staff_bp.route('/trek/<int:trek_id>')
@login_required
def trek_details(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        flash('You do not have permission to view this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))
    participants = Booking.query.filter(
        Booking.trek_id == trek_id,
        Booking.status.ilike('booked')
    ).all()
    return render_template('staff/trek_details.html', trek=trek, participants=participants)

@staff_bp.route('/trek/<int:trek_id>/update', methods=['POST'])
@login_required
def update_trek_status(trek_id):
    """Update trek slots and status (staff only for assigned treks)."""
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        flash('You are not assigned to this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))

    new_status = request.form.get('status', trek.status).lower()
    new_available = request.form.get('available_slots', type=int)

    # Validate status transitions
    valid_transitions = {
        'pending': ['open', 'closed'],
        'approved': ['open', 'closed'],
        'open': ['closed'],
        'closed': ['open', 'completed'],
    }

    current_status = trek.status.lower()
    if new_status != current_status:
        allowed = valid_transitions.get(current_status, [])
        if new_status not in allowed:
            flash(f'Cannot change status from "{trek.status}" to "{new_status}".', 'danger')
            return redirect(url_for('staff.trek_details', trek_id=trek_id))
        trek.status = new_status

        # If completed, mark all active bookings as completed
        if new_status == 'completed':
            active_bookings = Booking.query.filter(
                Booking.trek_id == trek_id,
                Booking.status.ilike('booked')
            ).all()
            for booking in active_bookings:
                booking.status = 'completed'

    if new_available is not None:
        if new_available < 0:
            flash('Available slots cannot be negative.', 'danger')
        else:
            trek.available_slots = new_available

    db.session.commit()
    flash(f'Trek "{trek.trek_name}" updated.', 'success')
    return redirect(url_for('staff.trek_details', trek_id=trek_id))

@staff_bp.route('/trek/<int:trek_id>/participants')
@login_required
def trek_participants(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        flash('You do not have permission to view participants for this trek.', 'danger')
        return redirect(url_for('staff.dashboard'))
    participants = Booking.query.filter(
        Booking.trek_id == trek_id,
        Booking.status.ilike('booked')
    ).all()
    return render_template('staff/trek_participants.html', trek=trek, participants=participants)
