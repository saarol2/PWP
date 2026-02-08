# PWP SPRING 2026
# Swimming baths reservation system
# Group information
* Oliver Saari, oliver.saari@student.oulu.fi
* Janne Tuikka, janne.tuikka@student.oulu.fi
* Minna Väänänen, minna.vaananen@student.oulu.fi

# 1. Dependency Information

Database used: SQLAlchemy with FLASK framework

Supported Platforms: SQLAlcehmy supports Python 3.7+ and Pypy  
Supported Databases: SQLite, Postgresql, MySQL & MariaDB, Oracle, MS-SQL  
Requirments for using database: DB-API 2.0 - Python Database API Specification  

[SQLAlchemy: Features https://www.sqlalchemy.org/features.html ]  
[Python Database API specification: https://peps.python.org/pep-0249/ ]



# 2. Instructions

Database instances: User, Reservation (has User and Timeslot), Timeslot (has Resource) and Resource.

How to create and populate database via ipython: 

from app import db, User, Resource, Timeslot, Reservation  
from app import app  
from datetime import datetime  
ctx = app.app_context()  
ctx.push()  
db.create_all()  

User:  
user1 = User(name="Jane Doe", email="my_email")  
db.session.add(user1)  
db.session.commit()  

Resource:  
res1 = Resource(name="bubble_bath", resource_type="pool")  
db.session.add(res1)  
db.session.commit()  

TimeSlot:  
time1 = Timeslot(  
    ...:     resource_id=res1.resource_id,  
    ...:     start_time=datetime(2018, 11, 21, 11, 20, 30),  
    ...:     end_time=datetime(2019, 11, 21, 10, 20, 30),  
    ...: )  
db.session.add(time1)  
db.session.commit()  

Reservation:  
reserv1 = Reservation(user_id=user1.user_id, slot_id=time1.slot_id, status="confirmed")  
db.session.add(reserv1)  
db.session.commit()  


User.query.all()  
`[<User Jane Doe>]`  
Resource.query.all()  
`[<Resource bubble_bath>]`  
Timeslot.query.all()  
`[<Timeslot 2018-11-21 11:20:30 - 2019-11-21 10:20:30>]`  
Reservation.query.all()  
`[<Reservation User 1 Slot 1>]`   






# 3.  
__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__


