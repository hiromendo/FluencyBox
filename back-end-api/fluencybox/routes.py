from flask import request, jsonify, make_response, Response, send_file, url_for
from sqlalchemy import or_
import base64
import os, io
import re
import csv
import json
from io import StringIO
from PIL import Image
from fluencybox import app, db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from fluencybox.models import User, User_Schema, Story, Story_Schema, Story_Scene, Story_Scene_Schema, Scene_Media, Scene_Media_Schema, Scene_Master_Response, Scene_Master_Response_Schema
from fluencybox.S3AssetManager import get_bucket, get_resource, save_avatar, save_story_object, delete_avatar, delete_story_object
from fluencybox.mailer import send_reset_email
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

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

#common method to generate tokens
def generate_tokens(uid):
    tokens = {}
    access_token = jwt.encode({'uid' : uid, 'token_type' : 'access_token' , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
    refresh_token = jwt.encode({'uid' : uid, 'token_type' : 'refresh_token' , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['REFRESH_TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
	
    tokens['access_token'] = access_token.decode('UTF-8')
    tokens['refresh_token'] = refresh_token.decode('UTF-8')

    return tokens

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

def get_paginated_list(page_object, object_type):
    try:
        resp_dict = {}
        output = []
        pagination = {}
        
        if object_type == 'user':
            for user in page_object.items:
                output.append({
                'uid' : user.uid, 
                'first_name' : user.first_name, 
                'last_name' : user.last_name, 
                'user_name' : user.user_name,
                'email_address' : user.email_address,
                'phone_number' : user.phone_number,
                'profile_picture' : user.profile_picture
                })
        elif object_type == 'story':
            for story in page_object.items:
                output.append({
                'uid' : story.uid, 
                'story_name' : story.story_name,
                'story_desc' : story.story_desc,
                'story_length' : story.story_length,
                'story_image' : story.story_image,
                'difficulty_level' : story.difficulty_level,
                'genre' : story.genre,
                })

        pagination['has_next'] = page_object.has_next
        pagination['has_prev'] = page_object.has_prev
        pagination['next_num'] = page_object.next_num
        pagination['page'] = page_object.page
        pagination['pages'] = page_object.pages
        pagination['per_page'] = page_object.per_page
        pagination['prev_num'] = page_object.prev_num
        pagination['total'] = page_object.total

        resp_dict['status'] = 'success'
        resp_dict['paginated_list'] = output
        resp_dict['pagination'] = pagination  
        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Get all users - paginate using page = 1 and per_page = 10 args in the URL
@app.route('/users',methods=['GET'])
@token_required
def get_all_users():
    try:
        resp_dict = {}
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        user_list = User.query.paginate(page = page, per_page = per_page)

        paginated_list = get_paginated_list(user_list, 'user')

        if paginated_list['status'] == 'success':
            resp_dict['status'] = 'success'
            resp_dict['users'] = paginated_list['paginated_list']
            resp_dict['pagination'] = paginated_list['pagination']
            return jsonify(resp_dict), 200
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = paginated_list['message']
            return jsonify(resp_dict), 500

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
        users_schema = User_Schema()
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
        email_address = user_data['email_address'].strip().lower() 
        user_name = user_data['user_name'].strip() 
        phone_number = user_data['phone_number'].strip() 

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

        tokens = generate_tokens(uid)
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']

        new_user = User(uid = uid, first_name = first_name, last_name = last_name, email_address = email_address, user_name = user_name, password = hashed_password, phone_number = phone_number, refresh_token = refresh_token)
        db.session.add(new_user)
        db.session.commit()

        resp_dict['status'] = 'success'
        resp_dict['message'] = 'New User Created'
        resp_dict['access_token'] = access_token
        resp_dict['refresh_token'] = refresh_token
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
        check_user_email = User.query.filter(User.email_address == user_data['email_address'].strip().lower()).filter(User.uid != uid.strip()).first()
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
        user.email_address = user_data['email_address'].strip().lower() 
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
        resp_dict['status'] = 'fail'
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
            tokens = generate_tokens(user.uid)
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']

            user.failed_login_attempts = 0
            user.refresh_token = refresh_token

            db.session.commit()

            resp_dict['status'] = 'success'
            resp_dict['access_token'] = access_token
            resp_dict['refresh_token'] = refresh_token
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
        tokens = generate_tokens(payload['uid'])
        new_access_token = tokens['access_token']
        new_refresh_token = tokens['refresh_token']
        
        #update new tokens in DB
        user.refresh_token = new_refresh_token
        db.session.commit()

        resp_dict['status'] = 'success'
        resp_dict['access_token'] = new_access_token
        resp_dict['refresh_token'] = new_refresh_token
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
        user = User.query.filter_by(email_address=user_data['email_address'].strip().lower()).first()
        
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

        user = User.query.filter_by(email_address = user_data['email_address'].strip().lower()).first()
        
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

#Story Routes
#Get all stories - paginate using page = 1 and per_page = 10 args in the URL
@app.route('/story',methods=['GET'])
@token_required
def get_all_story():
    try:
        resp_dict = {}
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        story_list = Story.query.paginate(page = page, per_page = per_page)
        
        paginated_list = get_paginated_list(story_list, 'story')

        if paginated_list['status'] == 'success':
            resp_dict['status'] = 'success'
            resp_dict['story'] = paginated_list['paginated_list']
            resp_dict['pagination'] = paginated_list['pagination']
            return jsonify(resp_dict), 200
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = paginated_list['message']
            return jsonify(resp_dict), 500

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Get a specific story
@app.route('/story/<uid>',methods=['GET'])
@token_required
def get_single_story(uid):
    try:
        resp_dict = {}
        story = Story.query.filter_by(uid = uid).first()
        
        if not story:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No story found'
            return jsonify(resp_dict),404
        story_schema = Story_Schema()
        story_data = story_schema.dump(story).data

        resp_dict['status'] = 'success'
        resp_dict['story'] = story_data
        
        return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Get story by filters
@app.route('/story_filter/',methods=['GET'])
@token_required
def get_filtered_story():
    try:
        resp_dict = {}
        difficulty_level  = request.args.get('difficulty_level', None)
        genre  = request.args.get('genre', None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if difficulty_level and genre:
            story_list = Story.query.filter(Story.difficulty_level == difficulty_level, Story.genre == genre).paginate(page = page, per_page = per_page)
        elif difficulty_level:
            story_list = Story.query.filter(Story.difficulty_level == difficulty_level).paginate(page = page, per_page = per_page)
        elif genre:
            story_list = Story.query.filter(Story.genre == genre).paginate(page = page, per_page = per_page)
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No parameters for query'
            return jsonify(resp_dict), 400
        
        if story_list.total < 1:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No story found'
            return jsonify(resp_dict),404

        paginated_list = get_paginated_list(story_list, 'story')

        if paginated_list['status'] == 'success':
            resp_dict['status'] = 'success'
            resp_dict['story'] = paginated_list['paginated_list']
            resp_dict['pagination'] = paginated_list['pagination']
            return jsonify(resp_dict), 200
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = paginated_list['message']
            return jsonify(resp_dict), 500

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

def insert_story(story_uid, story_name, story_desc, story_length, story_image, difficulty_level, genre):
    try:
        resp_dict = {}
        new_story = Story(uid = story_uid, story_name = story_name, story_desc = story_desc, story_length = story_length, story_image = story_image, difficulty_level = difficulty_level, genre = genre)
        db.session.add(new_story)

        resp_dict['status'] = 'success'
        resp_dict['new_story'] = new_story

        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def insert_scene(new_story, scene_order, scene_type, scene_keywords):
    try:
        resp_dict = {}
        if scene_type != 'FALSE' and scene_keywords != '':
            scene_uid = str(uuid.uuid4())
            new_scene = Story_Scene(uid = scene_uid, story = new_story, scene_order = scene_order, scene_type = scene_type, scene_keywords = scene_keywords)
            db.session.add(new_scene)
            
            resp_dict['status'] = 'success'
            resp_dict['new_scene'] = new_scene
        else:
            resp_dict['status'] = 'no insert'
        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def insert_media(story, scene_order, media_order, scene_image, scene_audio, scene_text, scene_hint, show_single):
    try:
        resp_dict = {}
        scene_media_uid = str(uuid.uuid4())

        #Get the scene that this media relates to
        story_scene = Story_Scene.query.filter(Story_Scene.story_id == story.id, Story_Scene.scene_order == scene_order).first()

        new_scene_media = Scene_Media(uid = scene_media_uid, story_scene = story_scene, media_order = media_order, scene_image = scene_image, scene_audio = scene_audio, scene_text = scene_text, scene_hint = scene_hint, show_single = show_single)
        db.session.add(new_scene_media)
        db.session.commit()

        resp_dict['status'] = 'success'
        resp_dict['message'] = 'success'

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def insert_master_response(master_audio_response, master_text_response, new_scene):
    try:
        resp_dict = {}
        if master_audio_response != '' and master_text_response != '':
            master_response_uid = str(uuid.uuid4())
            new_master_response = Scene_Master_Response(uid = master_response_uid, story_scene = new_scene, master_audio_response = master_audio_response, master_text_response = master_text_response)
            db.session.add(new_master_response)

            resp_dict['status'] = 'success'
            resp_dict['message'] = 'success'
            return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict
        
def upload_story_csv(story_csv):
    try:
        resp_dict = {}
        
        story_string = story_csv.read().decode('utf-8')
        story_csv = StringIO(story_string)
        reader = csv.DictReader(story_csv, delimiter=',')
        story_uid = str(uuid.uuid4()) #Create this outside the loop to use in the 2nd loop
        i = 0
        #Insert Story, Scene & Master Responses in this loop
        for row in reader:
            #if this is the first row, lets insert the main story data in the story table
            if i == 0:
                insert_story_response = insert_story(story_uid, row['story_name'].strip(), row['story_desc'].strip(), row['story_length'].strip(), row['story_image'].strip(), row['difficulty_level'].strip(), row['genre'].strip())
                if insert_story_response['status'] == 'success':
                    new_story = insert_story_response['new_story'] 

                #Insert the scene record & master response held in the first row
                insert_scene_response = insert_scene(new_story, row['scene_order'].strip(), row['scene_type'].strip(), row['scene_keywords'].strip())
                if insert_scene_response['status'] == 'success':
                    new_scene = insert_scene_response['new_scene'] 
                    insert_master_response(row['master_audio_response_1'].strip(), row['master_text_response_1'].strip(), new_scene)
                    insert_master_response(row['master_audio_response_2'].strip(), row['master_text_response_2'].strip(), new_scene)
                    insert_master_response(row['master_audio_response_3'].strip(), row['master_text_response_3'].strip(), new_scene)
                    insert_master_response(row['master_audio_response_4'].strip(), row['master_text_response_4'].strip(), new_scene)

            else:
                #Insert the scene and master response held after the first row
                insert_scene_response = insert_scene(new_story, row['scene_order'].strip(), row['scene_type'].strip(), row['scene_keywords'].strip())
                if insert_scene_response['status'] == 'success':
                    new_scene = insert_scene_response['new_scene']
                    insert_master_response(row['master_audio_response_1'].strip(), row['master_text_response_1'].strip(), new_scene)
                    insert_master_response(row['master_audio_response_2'].strip(), row['master_text_response_2'].strip(), new_scene)
                    insert_master_response(row['master_audio_response_3'].strip(), row['master_text_response_3'].strip(), new_scene)
                    insert_master_response(row['master_audio_response_4'].strip(), row['master_text_response_4'].strip(), new_scene)

            i = i + 1
        db.session.commit()

        #Re-initialize reader
        story_csv.seek(0)
        reader.__init__(story_csv, delimiter=",")

        #Get the id of the story inserted
        story = Story.query.filter_by(uid = story_uid).first()

        #Insert Scene Media and link with Story Id & Scene Order in this loop
        for row in reader:
            insert_media(story, row['scene_order'].strip(), row['media_order'].strip(), row['scene_image'].strip(), row['scene_audio'].strip(), row['scene_text'].strip(), row['scene_hint'].strip(), row['show_single'].strip())

        resp_dict['status'] = 'success'
        resp_dict['message'] = 'successfully uploaded'
        return resp_dict
      
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def upload_story_zip(story_zip):
    try:
        resp_dict = {}
        #Temporarily save zip the file to the bucket
        zip_upload_response = save_story_object(story_zip, story_zip.filename)
        if zip_upload_response['status'] == 'success':
            zip_url = zip_upload_response['object_url']
            #Open the URL pointing to the zip file
            zip_response = urlopen(zip_url)
            #Read the content to memory
            zip_file_content = ZipFile(BytesIO(zip_response.read()))
            #Loop through each file and save it to the bucket
            for file_name in zip_file_content.namelist():
                story_object = zip_file_content.open(file_name).read()
                upload_resp = save_story_object(story_object, file_name)
                if upload_resp['status'] != 'success':
                    resp_dict['status'] = 'fail'
                    resp_dict['message'] = upload_resp['message']
                    return resp_dict

        #Delete the zip file uploaded to the bucket
        delete_story_object(zip_url)
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'success'
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

@app.route('/upload_story', methods=['POST'])
@token_required
def upload_story():
    try:
        resp_dict = {}
        
        if 'story_zip' not in request.files:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No zip file found'
            return jsonify(resp_dict), 400

        if 'story_csv' not in request.files:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No csv file found'
            return jsonify(resp_dict), 400
        
        upload_zip_response = upload_story_zip(request.files['story_zip'])
        if upload_zip_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = upload_zip_response['message']
            return jsonify(resp_dict), 500

        upload_csv_response = upload_story_csv(request.files['story_csv'])
        if upload_csv_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = upload_csv_response['message']
            return jsonify(resp_dict), 500
        
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'story content uploaded successfully'
        return jsonify(resp_dict), 201

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500
