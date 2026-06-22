from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from app import models
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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

    pending_allotments = models.Trek.query.join(models.User).filter(models.User.is_blacklisted == True,
                                                                    models.Trek.status.in_(['Upcoming', 'Active'])).count()

    return render_template('admin/dashboard/dashboard.html', treks_count=total_treks, users_count=total_users, staff_count=total_staff, bookings_count=total_bookings, pending_count=pending_allotments)


''' All routes given below are related to Trek. manage_treks, create_trek, edit_trek, delete_trek'''

@admin_bp.route('/trek')
def manage_treks():
    
    # Displaying all the treks

    treks_list = models.Trek.query.all() # .query.all() will return results in a list format so we need to actually run a for loop to display all treks in a table. 

    return render_template('admin/trek/manage_treks.html', all_treks=treks_list) # Passing this list of treks to Jinja template in HTML


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

    available_staff = models.User.query.filter_by(role='Staff', is_blacklisted=False).all()
    return render_template('admin/trek/create_trek.html', trek=None, staff_members=available_staff)


@admin_bp.route('/trek/create/<int:trek_id>', methods=['GET', 'POST'])
def edit_trek(trek_id):

    # We use trek_id to fetch the exact Trek row from treks table, this will be useful when we have GET request. We need all this and form will be pre-filled

    trek_to_edit = models.Trek.query.get_or_404(trek_id)
    available_staff = models.User.query.filter_by(role='Staff', is_blacklisted=False).all()

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
    return render_template('admin/trek/create_trek.html', trek=trek_to_edit, staff_members=available_staff)


@admin_bp.route('/trek/delete/<int:trek_id>', methods=['POST'])
def delete_trek(trek_id):

    trek_to_delete = models.Trek.query.get_or_404(trek_id)

    models.db.session.delete(trek_to_delete)
    models.db.session.commit()

    flash(f"Trek {trek_to_delete.trek_name} has been removed Successfully!", "success")
    return redirect(url_for('admin.manage_treks'))



''' All routes given below are related to staff'''

@admin_bp.route('/staff')
def manage_staff():
    
    # Displaying profile of all staffs

    staff_list = models.User.query.filter_by(role='Staff').all()
    return render_template('admin/staff/manage_staff.html', all_staff=staff_list)


@admin_bp.route('/staff/addstaff', methods=['GET', 'POST'])
def add_staff():

    if request.method == 'POST':
        
        name = request.form.get('name')
        username = request.form.get('username')
        raw_password = request.form.get('password')
        contact_number = request.form.get('contact_number')

        # Doing the required validation checks on Phone number and username. len(contact_number) == 10 and it should be all digits. Need to check first if username exist already in users table if True then we ask to form a new username because username has Unique attibute to it. 

        if len(contact_number) != 10 or not contact_number.isdigit():
            flash("Contact number must be 10 digits", "danger")
            return redirect(url_for('admin.add_staff'))
        
        if models.User.query.filter_by(username=username).first(): # It means username already exist in users table
            flash("Username already exist. Choose another", "danger")
            return redirect(url_for('admin.add_staff'))
        
        # Hashing the raw password, only hashed passwords are saved in db not original one

        hashed_password = generate_password_hash(raw_password)

        # Now adding data to tables, We are adding data to 2 tables users and staff_profiles so need to create 2 object

        new_staff_user = models.User(username=username,
                                     password_hash=hashed_password,
                                     name=name,
                                     role='Staff',
                                     is_blacklisted=False)
        
        new_staff_profile = models.StaffProfile(user=new_staff_user,
                                                contact_number=contact_number,
                                                status='Active')
        
        models.db.session.add(new_staff_user)
        models.db.session.commit()

        flash(f"Staff member {name} added successfully!", "success")
        return redirect(url_for('admin.manage_staff'))
        
    return render_template('admin/staff/add_staff.html') # When it is a GET request we need to display HTML Form


@admin_bp.route('/staff/toggle/<int:staff_id>', methods=['POST'])
def toggle_staff_status(staff_id):

    staff_user = models.User.query.get_or_404(staff_id)

    # Before deactivating staff we will check if they have been already assigned to some upcoming/active trek

    if not staff_user.is_blacklisted:

        active_trek = models.Trek.query.filter(models.Trek.assigned_staff_id == staff_id, models.Trek.status.in_(['Upcoming', 'Active'])).first()

        if active_trek:
            flash(f"Staff {staff_user.name} has been deactivated but holds active treks reassign them.", "warning")
    
    # After above check we can switch the status
    staff_user.is_blacklisted = not staff_user.is_blacklisted

    if staff_user.staff_profile:
        staff_user.staff_profile.status = "Inactive" if staff_user.is_blacklisted else "Active"

    models.db.session.commit()
    return redirect(url_for('admin.manage_staff'))

