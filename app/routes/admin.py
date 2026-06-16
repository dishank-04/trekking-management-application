from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from app import models

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def admin_access():

    if 'user_id' not in session:

        flash("Access denied. Please login first")
        return redirect(url_for('auth.login'))
    
    if session.get('role') != 'Admin':

        flash("Not an Administrator")
        return redirect(url_for('auth.login'))


@admin_bp.route('/dashboard')
def admin_dashboard():

    total_treks = models.Trek.query.count()
    total_users = models.User.query.filter_by(role='Trekker').count()
    total_staff = models.User.query.filter_by(role='Staff').count()
    total_bookings = models.Booking.query.count()

    return render_template('admin/dashboard.html', treks_count=total_treks, users_count=total_users, staff_count=total_staff, bookings_count=total_bookings)

