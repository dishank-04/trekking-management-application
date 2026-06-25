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


MILESTONE - 3 Work 

We start with Admin dashboard and functionaltiy now. 

First thing we need is to actually authenticate that whether the user who is trying to access any url with '/admin' Prefix has role == 'admin' or not. This is important because and user with role staff or trekker should not be able to access anything related to /admin. 

To solve this issue we use something called .before_request() with admin blueprint, what it does is it will check whether role = 'admin' is the user who is trying to access any url with /admin. So it will be like barrier check before user gets access to /admin routes

-> Using SQLAlchemy to perform sql for us on Database and then we use Jinja template in dashboard.html to put values of the queries.


-> When using delete_trek() we need to keep in mind that trek_id which we delete will also exist in bookings table, we need to do cascading because treks is Parent Table and bookings is child table. Thus if we delete a trek me must delete all rows in bookings table with that trek_id or else there will be problems. 


Staff Related :-

-> We will not delete staff rather we will be just labelling them to Inactive when we make is_blacklisted = True for them. Once blacklisted staff shouldn't be visible in Create Trek form. 
But before making a staff memeber inactive we need to check that there are no active treks for them.


User Related :-

1) In manage_trekkers we are going to show these things to admin -> ID, Name, username, total_bookings, a/c status (Active or Blacklisted), Actions. Important thing is that User will register themselves, admin cannot add user. 

2) When we blacklist a trekker, we need to remove that trekker from all the 'Upcoming' treks not from Active and Completed ones but only for upcoming treks. And once we blacklist a trekker his booking is cancelled which cannot be redone even if he is unblacklisted. If Admin blacklists the user we show payment_status = 'Forfeited' but if User himself will cancel then we will show refund, but that part is for user routes.


ISSUE TO SOLVE -> WHEN USER BOOKS A TREK THE SLOTS_AVAILABLE DOESNT DECREASE IN TREKS CARD SOLVE IT. WE WILL SOLVE THIS ISSUE WHEN WE WILL MAKE ROUTES FOR TREKKER/USER NOT IN ADMIN PANEL.
