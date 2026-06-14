MILESTONE - 1 WORK

We use db.relationship() in Parent Table and then connect all other tables with Parent table

Why to use db.relationsip() when ForeignKey exist to connect Tables ?

-> A ForeignKey belongs strictly to database. This enforce the database to have user_id = 5 in it. But what if we try booking.user_id we get 5. 

But the thing is booking.user_id = 5 and user_id = 5 are not same thing for Python 5 is just a numerical value (integer) nothing more. To tell Python that 5 is user_id in table Users we need to use db.relationship() which will give some meaning to numbers returned by Database



Creating Pre-existing Admin using Python 

We do this in out main file app.py when web server starts then backend (Flask) will go to Python and there we will create Admin, If id does not exist already.

1) Now SQLALchemy used in models.py is Independent of Flask which we use in app.py. In models.py we used 'db' which is SQLAlchemy Object but it has no parameter in it. So db knows that we need to create Tables written in models.py but when we use browser it does not know how to access the tables from database

In main file 'app.py' we will provide parameter to it which is 'app' so that our SQLAlchemy will know that how to access database.


2) Now moving with Admin user creation -> When we run app.py first thing we need to do actaully is to tell our application where our database is going to be and what its name will be. 
nt User (Trekker) registration and login.
Because we are still not running web, Flask doesnt know which app we are trying to use so we need to create a proxy one using app_context() which requires a app.config['...'] = 'database' app.config tells to use that app and app_context() will use it. 


MILESTONE - 2 WORK 

1) Created RBAC (Role based Access) functionaltiy. Used Flask Blueprint for it. 

What is Flask Blueprint ?

-> WE can think of it like a mold, in which we code an entirely differnt thing and then use that blueprint inside our app to make it work. Blueprint on itself is not useful it has to be paired with app to actually make use of it.

Why to define app.config['SECRET_KEY'] = 'dev_secret_key_123' ? 

-> Browser is Client side, We as a developer cant do much with it. So when Server receives a request from Browser it will work on that request. But what if user went into Developer tools and changed role from 'Trekker' to 'Admin'. Server wont know anything and it will execute it, which will be catastrophioc.

-> To solve this issue everytime a request is sent by user, server checks that secret key and it helps server to realize whether it can execute that request or not. 








