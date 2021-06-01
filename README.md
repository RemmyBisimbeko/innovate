# innovate
A Simple web app built with flask to allow for self assessment of an Innovation Committee on Innovation Drives


# Instation
$ brew install python3
$ pip install Flask

# Initialization
$ Flask run

# Rename api_app
Rename api_app.py to app.py to access Restful API codebase


# REST API With Flask & SQL Alchemy

> loans API using Python Flask, SQL Alchemy and Marshmallow

## Quick Start Using Pipenv

``` bash
# Activate venv
$ pipenv shell

# Install dependencies
$ pipenv install

pip3 install pipenv
pipenv install flask
pipenv install flask-sqlalchemy
pipenv install flask-marshmallow
pipenv install marshmallow-sqlalchemy
pipenv install gunicorn 
pipenv install flask-mysqldb 
pipenv install wtforms
pipenv install flask-passlib
pipenv install python-dotenv  

# Create DB
$ python
>> from app import db
>> db.create_all()
>> exit()

# Run Server (http://localhst:5000)
python app.py
```

## Endpoints

* GET     /loan
* GET     /loan/:id
* POST    /loan
* PUT     /loan/:id
* DELETE  /loan/:id

## UI-SQL
# Install pip

# Install flask
$ pip install Flask


