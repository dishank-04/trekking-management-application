from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, db

authentication_bp = Blueprint('auth', __name__)

def redirect_active_user():

    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('auth.register'))

    current_user = User.query.get(user_id)

    if not current_user or current_user.is_blacklisted:
        session.clear()
        flash("Your account has been deactivated or blocked.", "danger")
        return redirect(url_for('auth.login'))

    role = current_user.role

    if role == 'Admin':
        return redirect(url_for('admin.admin_dashboard'))
    
    elif role == 'Staff':

        if current_user.staff_profile and current_user.staff_profile.status == "Pending_Active":
            flash("Update your password to continue", "warning")
            return redirect(url_for('staff.update_profile'))
        
        return redirect(url_for('staff.staff_dashboard'))
    
    elif role == 'Trekker':
        return redirect(url_for('trekker.trekker_dashboard'))
    

    
@authentication_bp.route('/')
def home():
    return redirect(url_for('auth.register'))



@authentication_bp.route('/login', methods=['GET', 'POST'])
def login():

    if 'user_id' in session:
        return redirect_active_user()

    if request.method == 'GET': 
        return render_template('authentication/login_test.html')

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):

        if user.role == "Pending_Approval":
            flash("Your application is under review by admin", "warning")
            return redirect(url_for('auth.login'))

        session['user_id'] = user.id
        session['role'] = user.role

        return redirect_active_user()

    flash('Invalid username or Password. Please enter valid credentials', 'danger')
    return redirect(url_for('auth.login'))



@authentication_bp.route('/register', methods=['GET','POST'])
def register():

    if 'user_id' in session:
        return redirect_active_user()

    if request.method == 'GET':
        return render_template('/authentication/register.html')

    name = request.form.get('name')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_passowrd = request.form.get('confirm_password')
    registration_role = request.form.get('registration_role')

    if password != confirm_passowrd:
        flash("Passwords do not match try again", "danger")
        return redirect(url_for('auth.register'))
    
    exisiting_user = User.query.filter_by(username=username).first()

    if exisiting_user:
        flash("Username already exist", "warning")
        return redirect(url_for('auth.register'))

    hashed_password = generate_password_hash(password)

    db_role = "Pending_Approval" if registration_role=="Trek Staff" else "Trekker"

    new_user = User(name=name,
                       username=username,
                       email_id=email,
                       password_hash=hashed_password,
                       role=db_role)
    
    db.session.add(new_user)
    db.session.commit()


    if db_role == "Pending_Approval":
        flash("Application Submitted Successfully. Please wait for Admin Approval.","success")
    else:
        flash("Account Created Successfully", "success")
    
    return redirect(url_for('auth.login'))




@authentication_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect(url_for('auth.login'))