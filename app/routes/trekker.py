from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from app import models
from werkzeug.security import generate_password_hash

trekker_bp = Blueprint('trekker', __name__, url_prefix='/trekker')


@trekker_bp.before_request
def trekker_access():

    if 'user_id' not in session:
        flash("Please Login first", "danger")
        return redirect(url_for('auth.login'))

    if session.get('role') != 'Trekker':
        flash("Access Denied you are not a trekker", "danger")
        return redirect(url_for('auth.login'))


@trekker_bp.route('/dashboard')
def trekker_dashboard():

    current_user = models.User.query.get(session['user_id'])
    trekker_name = current_user.name

    return render_template('/trekker/dashboard/dashboard.html', trekker_name=trekker_name)

''' All routes below are related to Explore Treks card '''

@trekker_bp.route('/explore')
def explore_treks():

    query = models.Trek.query.filter_by(status='Upcoming')

    search_name = request.args.get('search_name')
    location_filter = request.args.get('location')
    difficulty_filter = request.args.get('difficulty')

    if search_name:
        query = query.filter(models.Trek.trek_name.ilike(f"%{search_name}%"))

    if location_filter:
        query = query.filter(models.Trek.location.ilike(f"%{location_filter}%"))

    if difficulty_filter:
        query = query.filter(models.Trek.difficulty == difficulty_filter)

    
    upcoming_treks = query.all()

    return render_template('/trekker/explore_treks/explore_treks.html', 
                           upcoming_treks=upcoming_treks,
                           current_search=search_name,
                           current_location=location_filter,
                           current_difficulty=difficulty_filter)


@trekker_bp.route('/trek/<int:trek_id>')
def trek_detail(trek_id):

    trek = models.Trek.query.get_or_404(trek_id)
    return render_template('/trekker/explore_treks/trek_detail.html', trek=trek)



@trekker_bp.route('/checkout/<int:trek_id>')
def trek_checkout(trek_id):

    trek = models.Trek.query.get_or_404(trek_id)

    if trek.available_slots <= 0 or trek.status != 'Upcoming':
        flash("This Trek is not available", "danger")
        return redirect(url_for('trekker.explore_treks'))
    
    return render_template('/trekker/explore_treks/trek_checkout.html', trek=trek)



@trekker_bp.route('/process_payment/<int:trek_id>', methods=['POST'])
def process_payment(trek_id):

    trek = models.Trek.query.get_or_404(trek_id)    

    if trek.available_slots <= 0 or trek.status != 'Upcoming':
        flash("Transaction Failed, Trek sold out", "danger")
        return redirect(url_for('trekker.explore_treks'))
    
    
    existing_booking = models.Booking.query.filter_by(user_id = session['user_id'],
                                                      trek_id = trek.id).first()
    
    if existing_booking:
        flash("You have already booked this Trek", "warning")
        return redirect(url_for('trekker.explore_treks'))
    

    try:

        new_booking = models.Booking(user_id=session['user_id'],
                                     trek_id=trek.id,
                                     booking_status='Confirmed',
                                     payment_status='Completed')
        
        trek.available_slots -= 1

        models.db.session.add(new_booking)
        models.db.session.commit()

        flash("Payment Successfull","Success")

        return redirect(url_for('trekker.booking_history'))

    except Exception as e:

        flash("An Error occured. Please try again", "danger")
        return redirect(url_for('trekker.trek_checkout', trek_id=trek.id))
    

''' Below route is for user history '''

@trekker_bp.route('/history')
def booking_history():

    user_bookings = models.Booking.query.filter_by(user_id=session['user_id']).order_by(models.Booking.booking_date.desc()).all()

    return render_template('/trekker/booking_history/booking_history.html', bookings=user_bookings)
    


''' Below Route is for Updating User profile'''

@trekker_bp.route('/update_profile', methods=['GET', 'POST'])
def update_profile():

    current_user = models.User.query.get(session['user_id'])

    if request.method == 'POST':

        new_name = request.form.get('name')
        new_email = request.form.get('email')
        new_password = request.form.get('password')

        current_user.name = new_name
        current_user.email_id = new_email

        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
        
        models.db.session.commit()
        flash("Profile has been updated successfully", "success")

        return redirect(url_for('trekker.trekker_dashboard'))
    
    return render_template('/trekker/update_profile/update_profile.html', user=current_user)