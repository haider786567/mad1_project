from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from controller.auth import   login_required
from models import User, db,Booking, Trek
from werkzeug.security import generate_password_hash
user_bp = Blueprint('user', __name__)
@user_bp.route('/dashboard')
@login_required
def dashboard():
    availble_treks = Trek.query.filter_by(status='open').filter(Trek.available_slots > 0).order_by(Trek.created_at.desc()).all()
    Booked_treks = Booking.query.filter_by(user_id=current_user.id, status='booked').all()
    trek_status = {booking.trek_id: booking.status for booking in Booked_treks}
    recent_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).limit(5).all()
    return render_template('user/dashboard.html', 
                        treks=availble_treks, 
                        trek_status=trek_status,
                        Booked_treks=Booked_treks, 
                        recent_bookings=recent_bookings)
    
    
@user_bp.route('/treks/<int:trek_id>')
@login_required
def trek_details(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return render_template('user/trek_details.html', trek=trek)

@user_bp.route('/book/<int:trek_id>', methods=['POST'])
@login_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.status != 'open' or trek.available_slots <= 0:
        flash('This trek is not available for booking.', 'danger')
        return redirect(url_for('user.dashboard'))
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek_id).first()
    if existing_booking and existing_booking.status == 'booked':
        flash('You have already booked this trek.', 'info')
        return redirect(url_for('user.dashboard'))
    new_booking = Booking(user_id=current_user.id, trek_id=trek_id)
    db.session.add(new_booking)
    trek.available_slots -= 1
    db.session.commit()
    flash('Trek booked successfully!', 'success')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/bookings')
@login_required
def bookings():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('user/bookings.html', bookings=user_bookings)
@user_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('You do not have permission to cancel this booking.', 'danger')
        return redirect(url_for('user.bookings'))
    if booking.status != 'booked':
        flash('This booking cannot be canceled.', 'info')
        return redirect(url_for('user.bookings'))
    booking.status = 'canceled'
    trek = Trek.query.get(booking.trek_id)
    trek.available_slots += 1
    db.session.commit()
    flash('Booking canceled successfully.', 'success')
    return redirect(url_for('user.bookings'))

@user_bp.route('/history')
@login_required
def booking_history():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('user/booking_history.html', bookings=user_bookings)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        fullName = request.form.get('fullName')
        email = request.form.get('email')
        if not fullName or not email:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('user.profile'))
        
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            flash('Email is already in use by another account.', 'danger')
            return redirect(url_for('user.profile'))
        current_user.name = fullName
        current_user.email = email
        new_password = request.form.get('password')
        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return redirect(url_for('user.profile'))
            current_user.password = generate_password_hash(new_password)
        db.session.add(current_user)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', user=current_user)