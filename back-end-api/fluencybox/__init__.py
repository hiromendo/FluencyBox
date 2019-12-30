from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import create_database, database_exists
from flask_mail import Mail
from flask_cors import CORS, cross_origin
from flask_marshmallow import Marshmallow

application = Flask(__name__)
app = application
CORS(app)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
ma = Marshmallow(app)
mail = Mail(app)

if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
    create_database(app.config['SQLALCHEMY_DATABASE_URI'])
    if app.config['DEBUG']==1:
        from fluencybox.models import User
        dummy_user = User(uid='9c9f4d3c-62b7-4cab-b06b-14a82bd025b1', first_name = 'Hiro', last_name = 'Mendo', user_name = 'Hiro7', email_address = 'hiromendo@gmail.com', password = 'sha256$ID5K2eg5$1fdfd6afa111dae5599398ab0a0fb367e088e9d72b6dad887e5541d6727e9fa3', phone_number = '+1 23456789')
        db.session.add(dummy_user)
        db.session.commit()
        print("Dummy record inserted for Dev only - email - hiromendo@gmail.com & password - 12345")

if app.config['DEBUG']==1:
    from fluencybox.models import User
    admin = User.query.filter_by(user_name = 'admin').first()
    if not admin:
        admin_user = User(uid='1c9f4d3c-72b6-4cab-b06b-14a82bd025b2', first_name = 'Admin', last_name = 'M', user_name = 'admin', email_address = 'admin@gmail.com', password = 'sha256$ID5K2eg5$1fdfd6afa111dae5599398ab0a0fb367e088e9d72b6dad887e5541d6727e9fa3', phone_number = '+1 23456789', is_admin = 1)
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user inserted for Dev only - email - admin@gmail.com & user_name - admin & password - 12345")

from fluencybox import routes
