from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from app.models import User

authentication_bp = Blueprint('auth', __name__)

@authentication_bp.route('/')
def home():
    return redirect(url_for('auth.login'))


@authentication_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET': # If user is just sitting on Login Page or clicked to view Login page
        return render_template('authentication/login_test.html')

    # If user has clicked on 'Submit/Login' then its a post request. Thus we will get user's username and password from that POST request 

    username = request.form.get('username')
    password = request.form.get('password')

    # Now checking if user actually exist in User table or not 

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):

        # User exist in table thus we establish connection 

        session['user_id'] = user.id
        session['role'] = user.role

        if user.role == 'Admin':
            return redirect(url_for('admin.admin_dashboard'))
        

        elif user.role == 'Staff':

            if user.is_blacklisted:

                session.clear()

                flash("Your Account has been deactivated by Admin", "danger")
                return redirect(url_for('auth.login'))
            
            if user.staff_profile.status == "Pending_Active":

                flash("Update your passward to continue", "warning")
                return redirect(url_for('staff.update_profile'))
            
            elif user.staff_profile.status == "Active":

                return redirect(url_for('staff.staff_dashboard'))
            
        
        elif user.role == 'Trekker':
            return redirect(url_for('trekker_routes.dashboard'))

    flash('Invalid username or Password. Please enter valid credentials')
    return redirect(url_for('auth.login'))