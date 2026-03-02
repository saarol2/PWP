# PWP SPRING 2026
# Swimming baths reservation system
# Group information
* Oliver Saari, oliver.saari@student.oulu.fi
* Janne Tuikka, janne.tuikka@student.oulu.fi
* Minna Väänänen, minna.vaananen@student.oulu.fi

# 1. Dependency Information

- **Database:** SQLite  
- **ORM:** SQLAlchemy  
- **Web framework:** Flask
- **REST layer** Flask-RESTful
- **Caching**  Flask-Caching
- **Schema validation**  jsonschema

Supported Platforms: SQLAlchemy supports Python 3.7+ and Pypy  
Supported Databases: SQLite, Postgresql, MySQL & MariaDB, Oracle, MS-SQL  
Requirements for using database: DB-API 2.0 - Python Database API Specification  

[SQLAlchemy: Features](https://www.sqlalchemy.org/features.html)  
[Python Database API specification](https://peps.python.org/pep-0249/)

All dependencies are declared in [pyproject.toml](pyproject.toml). 




# 2.  Installation

### 2.1 Clone the repository 

```bash 

git clone <repository-url> 

cd PWP 

```

### 2.2 Create and activate a virtual environment 

```bash 

python -m venv .venv 

 

# Windows 

.venv\Scripts\activate 

 

# Linux / macOS 

source .venv/bin/activate 

```

### 2.3 Install the package 

 

Install the package and runtime dependencies: 

 

```bash 

pip install -e . 

``` 

 

Install the development/test dependencies: 

 

```bash 

pip install -e ".[dev]" 

```

## 3. Running the API 

 

The SQLite database (`instance/example.db`) is created automatically on first run. 

 

```bash 

flask --app swimapi run 

``` 

 

The API is now available at **http://127.0.0.1:5000**. 

 

### API Entrypoint 

 

| Collection | URL | 

|------------|-----| 

| Users | `GET/POST /api/users` | 

| User item | `GET/PUT/DELETE /api/users/<user_id>` | 

| Admin users | `GET /api/admin/users` | 

| Resources | `GET/POST /api/resources` | 

| Resource item | `GET/PUT/DELETE /api/resources/<resource_id>` | 

| Timeslots | `GET/POST /api/timeslots` | 

| Timeslot item | `GET/PUT/DELETE /api/timeslots/<slot_id>` | 

| Reservations | `GET/POST /api/reservations` | 

| Reservation item | `GET/PUT/DELETE /api/reservations/<reservation_id>` | 

 

--- 


# 4. Populate the database

The database tables are created automatically when the app starts. To add data manually use the Flask shell: 

```bash 

flask --app swimapi shell 

``` 

Database instances: User, Reservation, Timeslot and Resource.

## How to populate database via ipython: 
```python
from app import db, User, Resource, Timeslot, Reservation  
from app import app  
from datetime import datetime  
 
```
User:  
```python
user1 = User(name="Jane Doe", email="my_email")  
db.session.add(user1)  
db.session.commit()  
```
Resource:  
```python
res1 = Resource(name="bubble_bath", resource_type="pool")  
db.session.add(res1)  
db.session.commit()  
```
TimeSlot:  
```python
time1 = Timeslot(  
    ...:     resource_id=res1.resource_id,  
    ...:     start_time=datetime(2018, 11, 21, 11, 20, 30),  
    ...:     end_time=datetime(2019, 11, 21, 10, 20, 30),  
    ...: )  
db.session.add(time1)  
db.session.commit()  
```
Reservation:  
```python
reserv1 = Reservation(user_id=user1.user_id, slot_id=time1.slot_id, status="confirmed")  
db.session.add(reserv1)  
db.session.commit()  
```
Query data
```python
User.query.all()         # [<User Jane Doe>]
Resource.query.all()     # [<Resource bubble_bath>]
Timeslot.query.all()     # [<Timeslot 2018-11-21 11:20:30 - 2019-11-21 10:20:30>]
Reservation.query.all()  # [<Reservation User 1 Slot 1>]
```


## 5. Running Tests 

 

Test dependencies must be installed first (see section 2.3). 

 

Run the full test suite with coverage: 

 

```bash 

pytest 

``` 

Run a specific test file: 

 

```bash 

pytest tests/test_models.py -v 

```

Run only the resource API tests: 

 

```bash 

pytest tests/resources/ -v 

``` 

 

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__


