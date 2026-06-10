We use db.relationship() in Parent Table and then connect all other tables with Parent table


Why to use db.relationsip() when ForeignKey exist to connect Tables ?

-> A ForeignKey belongs strictly to database. This enforce the database to have user_id = 5 in it. But what if we try booking.user_id we get 5. 

But the thing is booking.user_id = 5 and user_id = 5 are not same thing for Python 5 is just a numerical value (integer) nothing more. TO tell Python that 5 is user_id in table Users we need to use db.relationship() which will give some meaning to numbers returned by Database

