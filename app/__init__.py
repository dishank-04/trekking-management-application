from flask import Flask
from app.models import db, User
from werkzeug.security import generate_password_hash

def create_app():

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///madproject.db' # Connecting flask with Database
    db.init_app(app) # Connecting Database (SQLAlchemy) with Flask

    with app.app_context():

        db.create_all() # Creating Physical tables

        admin_exist = User.query.filter_by(role='Admin').first()

        if not admin_exist:

            print("Admin does not exist, creating one ...")

            hashed_pass = generate_password_hash('admin123')

            admin_user_data = User(username='master_admin', password_hash=hashed_pass, name='System Admin', role='Admin')

            db.session.add(admin_user_data)
            db.session.commit()

            print("Admin user 'master_admin' created successfully")
        
        else:
            print("Admin already exist")
        
    return app