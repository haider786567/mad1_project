from flask import Blueprint, render_template, request, redirect, url_for, flash
from controller.auth import admin_required , login_required
from models import Trek, User,db, Booking
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/dashboard')
@admin_required
@login_required
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    pending_staff = User.query.filter_by(role='staff', status='pending').count()
    open_treks = Trek.query.filter(Trek.status.ilike('open')).count()
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    recent_treks = Trek.query.order_by(Trek.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                            total_treks=total_treks,
                            total_users=total_users,
                            total_staff=total_staff,
                            total_bookings=total_bookings,
                            pending_staff=pending_staff,
                            open_treks=open_treks,
                            recent_bookings=recent_bookings,
                            recent_treks=recent_treks
                    )

# ---------------------------------------------------------------------------
# Trek Management
# ---------------------------------------------------------------------------
@admin_bp.route('/treks')
@admin_required
@login_required
def trek_list():
    all_treks = Trek.query.all()
    staff_members = User.query.filter_by(role='staff', status='approved').all()
    return render_template('admin/trek_list.html', treks=all_treks, staff_members=staff_members)

@admin_bp.route('/treks/create', methods=['GET', 'POST'])
@admin_required
def create_trek():
    """Create a new trek."""
    if request.method == 'POST':
        trek_name = request.form.get('trek_name', '').strip()
        location = request.form.get('location', '').strip()
        difficulty = request.form.get('difficulty', 'Easy')
        duration = request.form.get('duration', type=int)
        available_slots = request.form.get('available_slots', type=int)
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'pending')

        if not all([trek_name, location, duration, available_slots is not None, start_date_str, end_date_str]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('admin.create_trek'))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('admin.create_trek'))

        if end_date < start_date:
            flash('End date must be after start date.', 'danger')
            return redirect(url_for('admin.create_trek'))

        trek = Trek(
            trek_name=trek_name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            start_date=start_date,
            end_date=end_date,
            description=description,
            status=status,
        )
        db.session.add(trek)
        db.session.commit()
        flash(f'Trek "{trek_name}" created successfully!', 'success')
        return redirect(url_for('admin.trek_list'))

    staff_list = User.query.filter_by(role='staff', status='approved').all()
    return render_template('admin/trek_form.html', trek=None, staff_list=staff_list)

@admin_bp.route('/treks/<int:trek_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_trek(trek_id):
    """Edit an existing trek."""
    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'POST':
        trek.trek_name = request.form.get('trek_name', '').strip()
        trek.location = request.form.get('location', '').strip()
        trek.difficulty = request.form.get('difficulty', 'Easy')
        trek.duration = request.form.get('duration', type=int)
        trek.available_slots = request.form.get('available_slots', type=int)
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        trek.description = request.form.get('description', '').strip()
        trek.status = request.form.get('status', trek.status)

        try:
            trek.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            trek.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('admin.edit_trek', trek_id=trek_id))

        db.session.commit()
        flash(f'Trek "{trek.trek_name}" updated successfully!', 'success')
        return redirect(url_for('admin.trek_list'))

    staff_list = User.query.filter_by(role='staff', status='approved').all()
    return render_template('admin/trek_form.html', trek=trek, staff_list=staff_list)

@admin_bp.route('/treks/<int:trek_id>/delete', methods=['POST'])
@admin_required
def delete_trek(trek_id):
    """Delete a trek and associated bookings."""
    trek = Trek.query.get_or_404(trek_id)
    Booking.query.filter_by(trek_id=trek_id).delete()
    db.session.delete(trek)
    db.session.commit()
    flash(f'Trek "{trek.trek_name}" has been deleted.', 'success')
    return redirect(url_for('admin.trek_list'))


@admin_bp.route('/treks/<int:trek_id>/assign-staff', methods=['POST'])
@admin_required
def assign_staff(trek_id):
    """Assign a staff member to a trek."""
    trek = Trek.query.get_or_404(trek_id)
    staff_id = request.form.get('staff_id', type=int)

    if staff_id:
        staff = User.query.get(staff_id)
        if staff and staff.role == 'staff' and staff.status == 'approved':
            trek.assigned_staff_id = staff_id
            db.session.commit()
            flash(f'Staff "{staff.name}" assigned to trek "{trek.trek_name}".', 'success')
        else:
            flash('Invalid staff member selected.', 'danger')
    else:
        trek.assigned_staff_id = None
        db.session.commit()
        flash(f'Staff unassigned from trek "{trek.trek_name}".', 'info')

    return redirect(url_for('admin.trek_list'))
# ---------------------------------------------------------------------------
# Staff Management
# ---------------------------------------------------------------------------

@admin_bp.route('/staff')
@admin_required
@login_required
def staff_list():
    staff_list = User.query.filter_by(role='staff').all()
    return render_template('admin/staff_list.html', staff_list=staff_list)

@admin_bp.route('/staff/<int:staff_id>/approve', methods=['POST'])
@admin_required
@login_required
def approve_staff(staff_id):
    staff = User.query.get_or_404(staff_id)
    if staff.role == 'staff':
        staff.status = 'approved'
        db.session.commit()
        flash('Staff member approved successfully.', 'success')
    return redirect(url_for('admin.staff_list'))

@admin_bp.route('/staff/<int:staff_id>/blacklist', methods=['POST'])
@admin_required
@login_required
def blacklist_staff(staff_id):
    staff = User.query.get_or_404(staff_id)
    if staff.role == 'staff':
        staff.status = 'blacklisted'
        db.session.commit()
        flash('Staff member blacklisted successfully.', 'success')
    return redirect(url_for('admin.staff_list'))

# ---------------------------------------------------------------------------
# User Management
# ---------------------------------------------------------------------------

@admin_bp.route('/users')
@admin_required
@login_required
def user_list():
    users = User.query.filter_by(role='user').all()
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/users/<int:user_id>/blacklist', methods=['POST'])
@admin_required
@login_required
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'user':
        user.status = 'blacklisted'
        db.session.commit()
        flash('User blacklisted successfully.', 'success')
    return redirect(url_for('admin.user_list'))


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------

@admin_bp.route('/bookings')
@admin_required
def bookings():
    """View all bookings."""
    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/booking.html', bookings=all_bookings)

# ---------------------------------------------------------------------------
# Search Functionality
# ---------------------------------------------------------------------------

@admin_bp.route('/search')
@admin_required
def search():
    """Search treks, staff, or users by name or ID."""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', 'all')

    treks = []
    staff_members = []
    users = []

    if query:
        # Search by ID (if numeric)
        is_numeric = query.isdigit()

        if category in ('all', 'treks'):
            trek_q = Trek.query
            if is_numeric:
                trek_q = trek_q.filter(
                    (Trek.id == int(query)) | Trek.trek_name.ilike(f'%{query}%') | Trek.location.ilike(f'%{query}%')
                )
            else:
                trek_q = trek_q.filter(Trek.trek_name.ilike(f'%{query}%') | Trek.location.ilike(f'%{query}%'))
            treks = trek_q.all()

        if category in ('all', 'staff'):
            staff_q = User.query.filter_by(role='staff')
            if is_numeric:
                staff_q = staff_q.filter(
                    (User.id == int(query)) | User.name.ilike(f'%{query}%') | User.email.ilike(f'%{query}%')
                )
            else:
                staff_q = staff_q.filter(User.name.ilike(f'%{query}%') | User.email.ilike(f'%{query}%'))
            staff_members = staff_q.all()

        if category in ('all', 'users'):
            user_q = User.query.filter_by(role='user')
            if is_numeric:
                user_q = user_q.filter(
                    (User.id == int(query)) | User.name.ilike(f'%{query}%') | User.email.ilike(f'%{query}%')
                )
            else:
                user_q = user_q.filter(User.name.ilike(f'%{query}%') | User.email.ilike(f'%{query}%'))
            users = user_q.all()

    return render_template('admin/search.html',
                           query=query,
                           category=category,
                           treks=treks,
                           staff_members=staff_members,
                           users=users)
