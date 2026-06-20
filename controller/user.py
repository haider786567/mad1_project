from flask import Blueprint, render_template, request, redirect, url_for, flash
from controller.auth import   login_required

user_bp = Blueprint('user', __name__)
@user_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('user/dashboard.html')