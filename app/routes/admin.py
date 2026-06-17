from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from app import models
from datetime import datetime

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


@admin_bp.route('/trek')
def manage_treks():
    
    # Displaying all the treks

    treks_list = models.Trek.query.all() # .query.all() will return results in a list format so we need to actually run a for loop to display all treks in a table. 

    return render_template('admin/manage_treks.html', all_treks=treks_list) # Passing this list of treks to Jinja template in HTML


@admin_bp.route('/trek/create', methods=['GET', 'POST'])
def create_trek():

    if request.method == 'POST':
        
        trek_name = request.form.get('trek_name')
        assigned_staff_id = int(request.form.get('assigned_staff_id'))
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        available_slots = int(request.form.get('available_slots'))
        status = request.form.get('status')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')

        # Before we add duration we need to check a condition on dates such that if end_date < start_date then we cannot proceed to calculate duration

        if end_date < start_date:
            flash("Failure, End date cannot be smaller than Start date", "danger")
            return redirect(url_for('admin.create_trek'))

        duration = (end_date - start_date).days


        # Now we have everthing to put into trek table 

        new_trek = models.Trek(trek_name=trek_name, 
                               assigned_staff_id=assigned_staff_id, 
                               location=location,
                               difficulty=difficulty,
                               duration=duration,
                               available_slots=available_slots,
                               status=status,
                               start_date=start_date,
                               end_date=end_date)

        models.db.session.add(new_trek)
        models.db.session.commit()

        flash(f"Trek {trek_name} created Successfully!", "success")
        return redirect(url_for('admin.manage_treks'))


    # If request method is Get which means that when admin click on +create new trek button he will be able to see a form open on screen

    available_staff = models.User.query.filter_by(role='Staff').all()
    return render_template('admin/create_trek.html', trek=None, staff_members=available_staff)


@admin_bp.route('trek/create/<int:trek_id>', methods=['GET', 'POST'])
def edit_trek(trek_id):

    # We use trek_id to fetch the exact Trek row from treks table, this will be useful when we have GET request. We need all this and form will be pre-filled

    trek_to_edit = models.Trek.query.get_or_404(trek_id)
    available_staff = models.User.query.filter_by(role='Staff').all()

    if request.method == 'POST':
        
        # We get the new data which admin wrote in HTML form

        new_trek_name = request.form.get('trek_name')
        new_assigned_staff_id = int(request.form.get('assigned_staff_id'))
        new_location = request.form.get('location')
        new_difficulty = request.form.get('difficulty')
        new_available_slots = int(request.form.get('available_slots'))
        new_status = request.form.get('status')
        new_start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        new_end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')

        # Validating Dates so that start_date > end_date is NOT TRUE 

        if new_start_date > new_end_date:
            flash("Failure, End date cannot be smaller than Start date", "danger")
            return redirect(url_for('admin.edit_trek', trek_id=trek_to_edit.id))
        
        new_duration = (new_end_date - new_start_date).days

        # Now we have new data with us all we need to do is modify data of trek_to_edit, do not create new data row

        trek_to_edit.trek_name = new_trek_name
        trek_to_edit.assigned_staff_id = new_assigned_staff_id
        trek_to_edit.location = new_location
        trek_to_edit.difficulty = new_difficulty
        trek_to_edit.available_slots = new_available_slots
        trek_to_edit.status = new_status
        trek_to_edit.start_date = new_start_date
        trek_to_edit.end_date = new_end_date
        trek_to_edit.duration = new_duration


        # Since we are not adding a new row to our treks table we dont need models.db.session.add() line we can directly commit the changes

        models.db.session.commit()

        flash(f"Trek {trek_to_edit.trek_name} updated Successfully!", "success")
        return redirect(url_for('admin.manage_treks'))


    # When we click on 'Edit' button server gets a GET request so we need to display form this line will do that
    return render_template('admin/create_trek.html', trek=trek_to_edit, staff_members=available_staff)
