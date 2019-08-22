from flask import request, jsonify, make_response, Response, send_file, url_for
from sqlalchemy import or_
import base64
import os, io
import re
from PIL import Image
from fluencybox import app, db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from fluencybox.models import User, user_schema
from fluencybox.S3AssetManager import get_bucket, get_resource, save_avatar, save_story_object, delete_avatar, delete_story_object
from fluencybox.mailer import send_reset_email

@app.route('/')
def index():
    return jsonify({'Page' : 'Index'})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = None
        
        resp_dict = {}

        if 'x-access-token' in request.headers:
            access_token = request.headers['x-access-token'].strip()

        if not access_token:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Token is invalid'
            return jsonify(resp_dict), 401
        
        try:
            payload = jwt.decode(access_token, app.config.get('SECRET_KEY'))
            if payload['token_type'] != 'access_token':
                resp_dict['status'] = 'fail'
                resp_dict['message'] = 'Token is invalid'
                return jsonify(resp_dict), 401
        except jwt.ExpiredSignatureError:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Token has expired'
            return jsonify(resp_dict), 401
        except jwt.InvalidTokenError:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Token is invalid'
            return jsonify(resp_dict), 401

        return f(*args, **kwargs)

    return decorated

def validate_email_address(email_address):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email_address)): 
        return True
    else:
        return False

def validate_user_name(user_name):
    regex = '^[A-Za-z0-9_-]+$'
    if(re.search(regex,user_name)): 
        return True
    else:
        return False

#Get all users
@app.route('/users',methods=['GET'])
@token_required
def get_all_users():
    try:
        resp_dict = {}
        users = User.query.all()
        users_schema = user_schema(many=True)
        output = users_schema.dump(users).data

        resp_dict['status'] = 'success'
        resp_dict['users'] = output

        return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500
        
#Changed after PR1 - uid'
#Get a specific user
@app.route('/users/<uid>',methods=['GET'])
@token_required
def get_single_user(uid):
    try:
        resp_dict = {}
        user = User.query.filter_by(uid = uid).first()
        
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404
        users_schema = user_schema()
        user_data = users_schema.dump(user).data

        resp_dict['status'] = 'success'
        resp_dict['user'] = user_data
        
        return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Create user - Registration. added confirm_password
@app.route('/users',methods=['POST'])
def create_user():
    try:
        resp_dict = {}
        user_data = request.get_json()
        #Check if all fields are present in JSON request 
        if not 'password' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No password in request'
            return jsonify(resp_dict),400

        if not 'confirm_password' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No confirm password in request'
            return jsonify(resp_dict),400

        if not 'first_name' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No first name in request'
            return jsonify(resp_dict),400
        
        if not 'last_name' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No last name in request'
            return jsonify(resp_dict),400

        if not 'email_address' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No email address in request'
            return jsonify(resp_dict),400
        
        if not 'user_name' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user name in request'
            return jsonify(resp_dict),400
        
        if not 'phone_number' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No phone number in request'
            return jsonify(resp_dict),400

        #check if password and confirm_password are same
        if user_data['password'].strip() != user_data['confirm_password'].strip():
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'password and confirm password do not match'
            return jsonify(resp_dict),400

        #checking password length
        if len(user_data['password'].strip()) < 8:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'password length must be at least 8 characters long'
            return jsonify(resp_dict),400
        
        #email validation
        is_valid_email_address = validate_email_address(user_data['email_address'].strip())
        if not is_valid_email_address:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'invalid email address'
            return jsonify(resp_dict),400

        #username validation
        is_valid_user_name = validate_user_name(user_data['user_name'].strip())
        if not is_valid_user_name:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'invalid user name'
            return jsonify(resp_dict),400

        hashed_password = generate_password_hash(user_data['password'].strip(), method='sha256')
        uid = str(uuid.uuid4())
        first_name = user_data['first_name'].strip() 
        last_name = user_data['last_name'].strip() 
        email_address = user_data['email_address'].strip() 
        user_name = user_data['user_name'].strip() 
        phone_number = user_data['phone_number'].strip() 
        access_token = jwt.encode({'uid' : uid, 'token_type' : 'access_token' , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
        refresh_token = jwt.encode({'uid' : uid, 'token_type' : 'refresh_token' , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['REFRESH_TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
		
        check_user_email = User.query.filter_by(email_address = email_address).first()
        if check_user_email:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Email already registered'
            return jsonify(resp_dict),400

        check_user_name = User.query.filter_by(user_name = user_name).first()
        if check_user_name:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'User name already registered'
            return jsonify(resp_dict),400
        
        new_user = User(uid = uid, first_name = first_name, last_name = last_name, email_address = email_address, user_name = user_name, password = hashed_password, phone_number = phone_number, refresh_token = refresh_token.decode('UTF-8'))
        db.session.add(new_user)
        db.session.commit()

        resp_dict['status'] = 'success'
        resp_dict['message'] = 'New User Created'
        resp_dict['access_token'] = access_token.decode('UTF-8')
        resp_dict['refresh_token'] = refresh_token.decode('UTF-8')
        resp_dict['uid'] = uid

        return jsonify(resp_dict),201
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Changed after PR1 - uid'
#Update user
@app.route('/users/<uid>',methods=['PUT'])
@token_required
def update_user(uid):
    try:
        resp_dict = {}
        
        user_data = request.get_json()
        #Check if all fields are present in JSON request
        if not 'first_name' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No first name in request'
            return jsonify(resp_dict),400
        
        if not 'last_name' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No last name in request'
            return jsonify(resp_dict),400

        if not 'email_address' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No email address in request'
            return jsonify(resp_dict),400
        
        if not 'user_name' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user name in request'
            return jsonify(resp_dict),400
        
        if not 'phone_number' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No phone number in request'
            return jsonify(resp_dict),400

        #email validation
        is_valid_email_address = validate_email_address(user_data['email_address'].strip())
        if not is_valid_email_address:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'invalid email address'
            return jsonify(resp_dict),400

        #username validation
        is_valid_user_name = validate_user_name(user_data['user_name'].strip())
        if not is_valid_user_name:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'invalid user name'
            return jsonify(resp_dict),400

        user = User.query.filter_by(uid = uid.strip()).first()

        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

        #Check if the username or email is shared with a different user
        check_user_email = User.query.filter(User.email_address == user_data['email_address'].strip()).filter(User.uid != uid.strip()).first()
        if check_user_email:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Email already registered'
            return jsonify(resp_dict),400

        check_user_name = User.query.filter(User.user_name == user_data['user_name'].strip()).filter(User.uid != uid.strip()).first()
        if check_user_name:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'User name already registered'
            return jsonify(resp_dict),400

        user.first_name = user_data['first_name'].strip() 
        user.last_name = user_data['last_name'].strip() 
        user.email_address = user_data['email_address'].strip() 
        user.user_name =  user_data['user_name'].strip() 
        user.phone_number = user_data['phone_number'].strip()

        db.session.commit()
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'User Updated Successfully'

        return jsonify(resp_dict),200
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Changed after PR1 - uid'. added confirm_password
#Update Password
@app.route('/users/<uid>/password',methods=['PUT'])
@token_required
def update_password(uid):
    try:
        resp_dict = {}
        user_data = request.get_json()
        #Check if password present in request
        if not 'password' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No password in request'
            return jsonify(resp_dict),400

        if not 'confirm_password' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No confirm password in request'
            return jsonify(resp_dict),400
        
        #check if password and confirm_password are same
        if user_data['password'].strip() != user_data['confirm_password'].strip():
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'password and confirm password do not match'
            return jsonify(resp_dict),400

        #checking password length
        if len(user_data['password'].strip()) < 8:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'password length must be at least 8 characters long'
            return jsonify(resp_dict),400

        user = User.query.filter_by(uid = uid.strip()).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

        hashed_password = generate_password_hash(user_data['password'].strip(), method='sha256')
        user.password = hashed_password
        user.refresh_token = null
        db.session.commit()
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'Password Updated Successfully'
        return jsonify(resp_dict),200
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Changed after PR1 - uid' -  changed profile_picture_file to profile_picture to match db col name
#Update Image
@app.route('/users/<uid>/profile_picture',methods=['PUT'])
@token_required
def update_profile_picture(uid):
    try:
        resp_dict = {}
        user = User.query.filter_by(uid = uid.strip()).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404
        
        if 'profile_picture' not in request.files:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No file found'
            return jsonify(resp_dict),400

        file = request.files['profile_picture']
        original_profile_picture = user.profile_picture
        
        save_object_response = save_avatar(file)
        
        if save_object_response['status'] == 'success':
            profile_picture = save_object_response['object_url']
            user.profile_picture = profile_picture
            db.session.commit()
            
            delete_avatar(original_profile_picture)

            resp_dict['status'] = 'success'
            resp_dict['message'] = 'successfully updated'
            resp_dict['profile_picture'] = profile_picture
            return jsonify(resp_dict),200
        elif save_object_response['status'] == 'fail':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = save_object_response['message']
            return jsonify(resp_dict),500

    except Exception as e:
        resp_dict['status'] = 'updatefail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Login
@app.route('/login',methods=['POST'])
def login():
    try:
        resp_dict = {}
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Invalid Credentials', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        
        #Allow user to log in with username or email address
        user = User.query.filter(or_ (User.email_address == auth.username.strip(), User.user_name == auth.username.strip())).first()
        if not user:
            return make_response('Invalid Credentials', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        
        if user.is_locked == 1:
            return make_response('Invalid Credentials', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

        if check_password_hash(user.password, auth.password.strip()):
            access_token = jwt.encode({'uid' : user.uid, 'token_type' : 'access_token' , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
            refresh_token = jwt.encode({'uid' : user.uid, 'token_type' : 'refresh_token' , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['REFRESH_TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
            
            user.failed_login_attempts = 0
            user.refresh_token = refresh_token.decode('UTF-8')

            db.session.commit()

            resp_dict['status'] = 'success'
            resp_dict['access_token'] = access_token.decode('UTF-8')
            resp_dict['refresh_token'] = refresh_token.decode('UTF-8')
            resp_dict['uid'] = user.uid
            return jsonify(resp_dict),200
        else:
            #If password is wrong, update failed counter in DB
            user.failed_login_attempts = user.failed_login_attempts + 1
            try:
                failed_login_attempts_lockout = int(app.config['FAILED_LOGIN_ATTEMPTS_LOCKOUT'])
                if failed_login_attempts_lockout == 0:
                    failed_login_attempts_lockout = 5
            except Exception as e:
                failed_login_attempts_lockout = 5

            if user.failed_login_attempts >= failed_login_attempts_lockout:
                user.is_locked = 1
            db.session.commit()

        return make_response('Invalid Credentials', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Changed after PR1 - uid/'token_type' : 'access_token'
#Refresh Token Request
@app.route("/access_tokens", methods=['POST'])
def refresh_token():
    try:
        x_refresh_token = None
        resp_dict = {}
        
        if 'x-refresh-token' in request.headers:
            x_refresh_token = request.headers['x-refresh-token'].strip()

        if not x_refresh_token:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Token is invalid'
            return jsonify(resp_dict), 401

        try:
            payload = jwt.decode(x_refresh_token, app.config.get('SECRET_KEY'))
        except jwt.ExpiredSignatureError:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Token is invalid'
            return jsonify(resp_dict), 401
        except jwt.InvalidTokenError:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Token is invalid'
            return jsonify(resp_dict), 401

        user = User.query.filter_by(refresh_token = x_refresh_token).first()
        #if a user with the refresh_token is not found in the DB, return failure and user will have to login again 
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Token is invalid'
            return jsonify(resp_dict), 401

        #if a valid refresh_token is found in the DB, create a new access & refresh token, update in DB and return to front end
        new_access_token = jwt.encode({'uid' : payload['uid'], 'token_type' : 'access_token' ,  'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
        new_refresh_token = jwt.encode({'uid' : payload['uid'], 'token_type' : 'refresh_token' ,  'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['REFRESH_TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])

        #update new tokens in DB
        user.refresh_token = new_refresh_token.decode('UTF-8')
        db.session.commit()

        resp_dict['status'] = 'success'
        resp_dict['access_token'] = new_access_token.decode('UTF-8')
        resp_dict['refresh_token'] = new_refresh_token.decode('UTF-8')
        resp_dict['uid'] = payload['uid']
        return jsonify(resp_dict),200
        
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Changed after PR1 - email_address
#Sends the email for the password reset if email is registered
@app.route("/reset_password", methods=['POST'])
def reset_request():
    try:
        resp_dict = {}
        
        user_data = request.get_json()
        #Check if email present in request
        if not 'email_address' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No email in request'
            return jsonify(resp_dict),400
        user = User.query.filter_by(email_address=user_data['email_address'].strip()).first()
        
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404
        
        send_reset_email(user)

        resp_dict['status'] = 'success'
        resp_dict['message'] = 'An email has been sent with instructions to reset your password.'
        return jsonify(resp_dict),200
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Link in email comes to this route and validates the token
@app.route("/reset_password/<token>", methods=['GET'])
def reset_token(token):
    try:
        resp_dict = {}
        user = User.verify_reset_token(token)
        if user is None:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'That is an invalid or expired token'
            return jsonify(resp_dict),401
        
        resp_dict['status'] = 'success'
        resp_dict['email_address'] = user.email_address
        resp_dict['message'] = 'Enter New Password'
        return jsonify(resp_dict),200
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500  

#Changed after PR1 - /password_reset. added confirm_password
#Update Password after entering new password
@app.route('/password_reset',methods=['PUT'])
def reset_password():
    try:
        resp_dict = {}
        user_data = request.get_json()
        #Check if password present in request
        if not 'password' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No password in request'
            return jsonify(resp_dict),400

        if not 'confirm_password' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No confirm password in request'
            return jsonify(resp_dict),400

        #check if password and confirm_password are same
        if user_data['password'].strip() != user_data['confirm_password'].strip():
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'password and confirm password do not match'
            return jsonify(resp_dict),400

        #checking password length
        if len(user_data['password'].strip()) < 8:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'password length must be at least 8 characters long'
            return jsonify(resp_dict),400

        if not 'email_address' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No email address in request'
            return jsonify(resp_dict),400

        user = User.query.filter_by(email_address = user_data['email_address'].strip()).first()
        
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

        hashed_password = generate_password_hash(user_data['password'].strip(), method='sha256')
        user.password = hashed_password
        user.is_locked = 0
        user.failed_login_attempts = 0
        user.refresh_token = null

        db.session.commit()
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'Password Updated Successfully'
        return jsonify(resp_dict),200
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500
