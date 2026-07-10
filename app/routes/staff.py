from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from app import models
from werkzeug.security import generate_password_hash,check_password_hash


staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.before_request
def staff_hold():

    if 'user_id' not in session or session.get('role') != 'Staff':

        flash("Unauthorized Access, relogin", "danger")
        return redirect(url_for('auth.login'))

    current_staff_user = models.User.query.get(session['user_id']) # Searches using Primary ID helps with performance boost


    if current_staff_user.staff_profile.status == "Pending_Active":

        allowed_endpoints = ['staff.update_profile', 'auth.logout']

        if request.endpoint not in allowed_endpoints:
            flash("You must finalize your profile first", "warning")
            return redirect(url_for('staff.update_profile'))



@staff_bp.route('/update_profile', methods=['GET', 'POST'])
def update_profile():

    current_staff_user = models.User.query.get(session['user_id'])
    is_joining = current_staff_user.staff_profile.status == 'Pending_Active'

    if request.method == 'POST':


        email = request.form.get('email')
        old_passowrd = request.form.get('old_password')
        new_password = request.form.get('new_password')
        contact_number = request.form.get('contact_number')

        if len(contact_number) != 10 or not contact_number.isdigit():

            flash("Invalid Format of contact number", "danger")
            return redirect(url_for('staff.update_profile'))
        

        if is_joining:

            if not new_password or len(new_password) < 6:
                flash("Password must be atleast 6 characters long","danger")
                return redirect(url_for('staff.update_profile'))
            
            current_staff_user.password_hash = generate_password_hash(new_password)
            current_staff_user.staff_profile.status = 'Active'

            flash(f"Welcome to Dashboard {current_staff_user.name}","success")

        else:
                
            if new_password: # Password update is optional we dont need password to get updated if user doesnt want
                
                if not check_password_hash(current_staff_user.password_hash, old_passowrd):
                    flash("Wrong Old Password. Please try again.", "danger")
                    return redirect(url_for('staff.update_profile'))
                
                if new_password == old_passowrd:
                    flash("New password cannot be the same as the old password.", "warning")
                    return redirect(url_for('staff.update_profile'))

                if len(new_password) < 6:
                    flash("New password must be at least 6 characters.", "danger")
                    return redirect(url_for('staff.update_profile'))

                current_staff_user.password_hash = generate_password_hash(new_password)
            
        
        flash("Profile Updated Successfully", "success")
        
        current_staff_user.staff_profile.contact_number = contact_number
        current_staff_user.email_id = email

        models.db.session.commit()

        return redirect(url_for('staff.staff_dashboard'))

    # For GET Request
    return render_template('staff/update_profile.html', user=current_staff_user, is_joining=is_joining)



@staff_bp.route('/dashboard')
def staff_dashboard():

    staff_id = session['user_id']
    staff_user = models.User.query.get(staff_id)

    active_treks_count = models.Trek.query.filter(models.Trek.assigned_staff_id == staff_id,
                                                  models.Trek.status.in_(['Upcoming', 'Active'])).count()
    
    completed_treks_count = models.Trek.query.filter(models.Trek.assigned_staff_id == staff_id, 
                                                     models.Trek.status == 'Completed').count()
    
    next_trek = models.Trek.query.filter(models.Trek.assigned_staff_id == staff_id,
                                         models.Trek.status == 'Upcoming').order_by(models.Trek.start_date.asc()).first()

    all_assigned_treks = models.Trek.query.filter_by(assigned_staff_id=staff_id).all()

    trek_names = [trek.trek_name for trek in all_assigned_treks]
    participant_counts = [len([b for b in trek.bookings if b.booking_status != 'Cancelled']) for trek in all_assigned_treks]

    
    return render_template('/staff/dashboard/dashboard.html', 
                           staff_user=staff_user, 
                           active_count=active_treks_count, 
                           completed_count=completed_treks_count, 
                           next_trek=next_trek,
                           trek_names=trek_names,
                           participant_counts=participant_counts)



@staff_bp.route('/assigned_treks')
def assigned_treks():

    treks = models.Trek.query.filter(models.Trek.status.in_(['Upcoming','Active']),
                                     models.Trek.assigned_staff_id == session['user_id']).order_by(models.Trek.start_date.asc()).all()
    
    return render_template('/staff/assigned_treks/assigned_treks.html', assigned_treks=treks)
    

''' All routes below are part of Assigned Treks '''

@staff_bp.route('/manage_trek/<int:trek_id>', methods=['GET','POST'])
def manage_treks(trek_id):

    trek = models.Trek.query.filter_by(assigned_staff_id=session['user_id'], id=trek_id).first_or_404()


    if request.method == "POST":

        slots = request.form.get('available_slots')
        new_status = request.form.get('status')

        if not slots or int(slots) < 0:

            flash("Slots cannot be empty or negative", "danger")
            return redirect(url_for('staff.manage_treks', trek_id=trek.id))
        

        new_slots = int(slots)

        if new_status == 'Active' and trek.status != 'Active': # We search for other treks where staff might be active

            exisiting_active_trek = models.Trek.query.filter_by(assigned_staff_id=session['user_id'], status='Active').first()

            if exisiting_active_trek:
                flash(f"You already have an active trek {exisiting_active_trek.trek_name} you cannot Activate this trek before completing it", "danger")
                return redirect(url_for('staff.manage_treks', trek_id=trek.id))

        
        if new_status == 'Completed' and trek.status != 'Completed':
            models.Booking.query.filter_by(trek_id=trek.id, booking_status='Confirmed').update({"booking_status":"Completed"}) # We filter using booking_status='Confirmed' so that if user cancelled their bookings before we dont have to change their cancelled status


        trek.available_slots = new_slots
        trek.status = new_status

        models.db.session.commit()

        flash(f"Trek {trek.trek_name} updated successfully", "success")
        return redirect(url_for('staff.assigned_treks'))


    return render_template('/staff/assigned_treks/manage_treks.html', trek=trek)



@staff_bp.route('/manage_participants/<int:trek_id>')
def manage_participants(trek_id):
    
    trek = models.Trek.query.filter_by(id=trek_id, assigned_staff_id=session['user_id']).first_or_404()

    bookings = models.Booking.query.join(models.User).filter(models.Booking.trek_id==trek_id).all()

    return render_template('/staff/assigned_treks/manage_participants.html', trek=trek, bookings=bookings)



@staff_bp.route('/participant/cancel/<int:booking_id>', methods=['POST'])
def cancel_participant(booking_id):

    booking = models.Booking.query.get_or_404(booking_id)

    if booking.trek.assigned_staff_id != session['user_id']:
        flash("You cannot access this")
        return redirect(url_for('staff.assigned_treks'))
    
    if booking.trek.status == 'Completed':
        flash("Trek is already Completed", "danger")
        return redirect(url_for('staff.trek_participants', trek_id=booking.trek_id))

    if booking.booking_status != 'Confirmed':
        flash("Participant is not in a Confirmed state.", "warning")
        return redirect(url_for('staff.trek_participants', trek_id=booking.trek_id))
    
    booking.booking_status = 'Cancelled'
    booking.payment_status = 'Forfeited'
    booking.trek.available_slots += 1

    models.db.session.commit()

    flash(f"Participant {booking.trekker.name} has been marked Absent", "success")

    return redirect(url_for('staff.manage_participants', trek_id=booking.trek_id))


''' All routes below are part of Trek History '''

@staff_bp.route('/trek_history')
def trek_history():

    treks = models.Trek.query.filter_by(status='Completed', assigned_staff_id=session['user_id'])

    return render_template('/staff/trek_history/trek_history.html', treks=treks)



@staff_bp.route('/trek/participants_history/<int:trek_id>', methods=['GET'])
def trek_participants_history(trek_id):
 
    trek = models.Trek.query.filter_by(id=trek_id, assigned_staff_id=session['user_id']).first_or_404()

    bookings = models.Booking.query.join(models.User).filter(models.Booking.trek_id==trek_id).all()

    return render_template('/staff/trek_history/trek_participants_history.html', trek=trek, bookings=bookings)