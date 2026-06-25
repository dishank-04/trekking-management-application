from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from app import models
from datetime import datetime
from werkzeug.security import generate_password_hash

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

    search_term = request.args.get('search')
    query = models.Trek.query

    if search_term:

        if search_term.isdigit():
            query = query.filter(models.Trek.id == int(search_term))
        
        else:
            query = query.filter(models.Trek.trek_name.ilike(f"%{search_term}%"))

    # Displaying all the treks

    treks_list = query.all() # .query.all() will return results in a list format so we need to actually run a for loop to display all treks in a table. 
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



''' All routes given below are related to staff which include manage_staff, adding_staff, Deactivate Staff, pending allotments of deactivated staff and reassigning those treks to new staff'''

@admin_bp.route('/staff')
def manage_staff():

    search_term = request.args.get('search')
    query = models.User.query.filter_by(role='Staff')

    if search_term:

        if search_term.isdigit():
            query = query.filter(models.User.id == int(search_term))
        
        else:
            query = query.filter(models.User.name.ilike(f"%{search_term}%"))


    staff_list = query.all()
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

    # We are not going to delete Staff from db rather we will just deactivate that staff member, because we need staff's id to actualyl get history and booking part. 

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



@admin_bp.route('/staff/pending_allotments')
def staff_pending():

    # This is a strictly GET method we are not doing reassigment here all we are doing is just display the allotments which needs to be reassigned.
    
    pending_treks = models.Trek.query.join(models.User).filter(models.User.is_blacklisted == True,
                                                                    models.Trek.status.in_(['Upcoming', 'Active'])).all()
    
    available_staff = models.User.query.filter_by(role='Staff', is_blacklisted=False).all()
    
    return render_template('admin/staff/pending_staff_allotments.html', pending_treks=pending_treks, active_staff=available_staff)



@admin_bp.route('/staff/reassign_staff/<int:trek_id>', methods=['POST'])
def reassign_staff(trek_id):

    raw_staff_id = request.form.get('new_staff_id')
    new_staff_id = int(raw_staff_id)

    # We need to check if the new_staff_id which we got is still valid or not because what if admin changes new_staff and its blacklisted while he simultaneously try to put that new_staff ro reassignment

    valid_staff = models.User.query.filter_by(id=new_staff_id, role='Staff', is_blacklisted=False).first()

    # Now we can update our Trek

    trek_to_update = models.Trek.query.get_or_404(trek_id)
    trek_to_update.assigned_staff_id = valid_staff.id

    models.db.session.commit()

    flash(f"Successfully Reassigned {trek_to_update.trek_name} to {valid_staff.name}", "success")
    return redirect(url_for('admin.staff_pending'))



''' All below routes are realted to Trekkers/users '''

@admin_bp.route('/trekkers')
def manage_trekkers():

    search_term = request.args.get('search')
    query = models.User.query.filter_by(role='Trekker')

    if search_term:
        
        # If admin searches using id then
        if search_term.isdigit():
            query = query.filter(models.User.id == int(search_term))
        
        # Admin is searching using alphabets
        else:
            query = query.filter(models.User.name.ilike(f"%{search_term}%"))
    
    
    trekkers_list = query.all() # If there is no search term we give all the Trekkers to admin

    return render_template('/admin/trekkers/manage_trekkers.html', all_trekkers=trekkers_list)



@admin_bp.route('/trekkers/toggle/<int:trekker_id>', methods=['POST'])
def toggle_trekker_status(trekker_id):
    
    trekker_user = models.User.query.get_or_404(trekker_id)
    trekker_user.is_blacklisted = not trekker_user.is_blacklisted

    if trekker_user.is_blacklisted:

        upcoming_bookings = models.Booking.query.join(models.Trek).filter(models.Trek.status == 'Upcoming', 
                                                                          models.Booking.booking_status == 'Confirmed',
                                                                          models.Booking.user_id == trekker_id).all()
        

        for booking in upcoming_bookings:

            booking.booking_status = 'Cancelled'
            booking.payment_status = 'Forfeited'
            booking.trek.available_slots += 1
        

        if upcoming_bookings:
            flash(f"Trekker {trekker_user.name} has been Blacklisted {len(upcoming_bookings)} bookings have been cancelled", "danger")

        else:
            flash(f"Trekker {trekker_user.name} has been Blacklisted", "danger")
    
    
    models.db.session.commit()

    return redirect(url_for('admin.manage_trekkers'))


@admin_bp.route('/trekkers/<int:trekker_id>/history')
def view_trekker_history(trekker_id):

    trekker_user = models.User.query.get_or_404(trekker_id)

    booking_history = (models.Booking.query.filter_by(user_id=trekker_id)
                       .join(models.Trek)
                       .order_by(models.Trek.start_date.desc())
                       .all()
                      ) 
    
    return render_template('/admin/trekkers/view_trekker_history.html', trekker=trekker_user, history=booking_history)



''' All routes given below are related to bookings '''

@admin_bp.route('/bookings')
def manage_bookings():

    all_bookings = models.Booking.query.join(models.User, models.Booking.user_id == models.User.id).join(models.Trek, models.Booking.trek_id == models.Trek.id).order_by(models.Booking.booking_date.desc()).all()

    return render_template('/admin/bookings/manage_bookings.html', all_bookings=all_bookings)


@admin_bp.route('/bookings/forcecancel/<int:booking_id>', methods=['POST'])
def force_cancel_booking(booking_id):

    booking_to_cancel = models.Booking.query.get_or_404(booking_id)

    if booking_to_cancel.booking_status != 'Confirmed' or booking_to_cancel.trek.status != 'Upcoming':
        flash("Only Confirmed Bookings for Upcoming treks can be cancelled")
        return redirect(url_for('admin.manage_bookings'))

    booking_to_cancel.booking_status = 'Cancelled'
    booking_to_cancel.trek.available_slots += 1
    booking_to_cancel.payment_status = 'Forfeited'

    models.db.session.commit()

    flash(f"Booking {booking_to_cancel.id} for user {booking_to_cancel.trekker.name} has been force cancelled", "warning")
    return redirect(url_for('admin.manage_bookings'))