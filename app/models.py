from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


# Creating required Tables

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(8>0), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)


    # Defining Relationships between Tables for Python to understand them

    staff_profile = db.relationship('StaffProfile', backref='user', uselist=False, cascade='all, delete-orphan') # userlist =False strictly enforces a 1-to-1 relatiosnhip b/w users and staff_profiles table
    bookings = db.relationship('Booking', backref='trekker', lazy=True) # lazy=True Parameter is used tell SQLAlchemy that until i specifically state a python code like user.bookings do not run SQL Query 



class StaffProfile(db.Model):

    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    contact_number = db.Column(db.String(15), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)


class Trek(db.Model):

    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(200), nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)


    # Relationships among Tables 
    
    bookings = db.relationship('Booking', backref='trek', lazy=True, cascade='all, delete-orphan')
    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id])


class Booking(db.Model):

    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_status = db.Column(db.String(20), default='Confirmed')
    payment_status = db.Column(db.String(20), default='Pending')
    booking_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) # using datetime.now(timezone.utc) with lambda, this will act as a function and every time a new row is inserted it will automatically take the correct time
