from flask import request, jsonify, make_response, Response, send_file, url_for
from sqlalchemy import or_
import base64
import os, io
import re
import json
from io import StringIO
from PIL import Image
from fluencybox import app, db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from fluencybox.models import User, User_Schema, Story, Story_Schema, Story_Scene, Story_Scene_Schema, \
Scene_Keyword, Scene_Keyword_Schema, Story_Scene_Speaker, Story_Scene_Speaker_Schema, \
Story_Scene_Master_Response, Story_Scene_Master_Response_Schema, User_Story, User_Story_Schema, \
Story_Scene_User_Response, Story_Scene_User_Response_Schema, Report, Report_Schema, \
Report_Images, Report_Images_Schema, Story_Purchase, Story_Purchase_Schema, User_Purchase, User_Purchase_Schema
from fluencybox.S3AssetManager import get_bucket, get_resource, save_avatar, save_story_object, delete_avatar, delete_story_object, generate_presigned_url
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
                image_filename = generate_presigned_url(app.config.get('S3_BUCKET'), app.config.get('S3_CONTENT_DIR')+'/'+story.image_filename)
                output.append({
                'uid' : story.uid, 
                'name' : story.name,
                'description' : story.description,
                'length' : story.length,
                'image_filename' : image_filename,
                'difficulty' : story.difficulty,
                'genre' : story.genre,
                'is_demo': story.is_demo
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

        #Check if current password in request
        if not 'current_password' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No current password in request'
            return jsonify(resp_dict),400

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
        
        #checking whether the current password from user matches the password saved in the DB
        if not check_password_hash(user.password, user_data['current_password'].strip()):
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Invalid Credentials'
            return jsonify(resp_dict),401

        hashed_password = generate_password_hash(user_data['password'].strip(), method='sha256')
        user.password = hashed_password
        user.refresh_token = ''
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
        user.refresh_token = ''

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

        story_data['image_filename'] = generate_presigned_url(app.config.get('S3_BUCKET'), app.config.get('S3_CONTENT_DIR')+'/'+story_data['image_filename'])
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
        difficulty  = request.args.get('difficulty', None)
        genre  = request.args.get('genre', None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if difficulty and genre:
            story_list = Story.query.filter(Story.difficulty == difficulty, Story.genre == genre).paginate(page = page, per_page = per_page)
        elif difficulty:
            story_list = Story.query.filter(Story.difficulty == difficulty).paginate(page = page, per_page = per_page)
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

def insert_story(name, description, length, image_filename, difficulty, genre, is_demo):
    try:
        resp_dict = {}
        uid = str(uuid.uuid4())
        new_story = Story(uid = uid, name = name, description = description, length = length, image_filename = image_filename, difficulty = difficulty, genre = genre, is_demo = is_demo)
        db.session.add(new_story)
        db.session.commit()
        resp_dict['status'] = 'success'
        resp_dict['new_story'] = new_story
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def insert_story_scene(new_story, order, type, next_scene_order):
    try:
        resp_dict = {}
        uid = str(uuid.uuid4())
        new_scene = Story_Scene(uid = uid, story = new_story, order = order, type = type, next_scene_order = next_scene_order)
        db.session.add(new_scene)
        db.session.commit()
        resp_dict['status'] = 'success'
        resp_dict['new_scene'] = new_scene
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def insert_scene_keyword(new_scene, keyword_list):
    try:
        resp_dict = {}
        for keyword in keyword_list:
            new_keyword = Scene_Keyword(story_scene = new_scene, keyword = keyword['keyword'], next_scene_order = keyword['next_scene_order'])
            db.session.add(new_keyword)
            db.session.commit()
        resp_dict['status'] = 'success'
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def insert_story_scene_speaker(new_scene, order, image_filename, audio_filename, audio_text, prompt):
    try:
        resp_dict = {}
        new_story_scene_speaker = Story_Scene_Speaker(story_scene = new_scene, order = order, image_filename = image_filename, audio_filename=audio_filename, audio_text = audio_text, prompt = prompt)
        db.session.add(new_story_scene_speaker)
        db.session.commit()
        resp_dict['status'] = 'success'
        resp_dict['new_story_scene_speaker'] = new_story_scene_speaker
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def insert_story_scene_master_responses(new_story_scene_speaker, audio_filename, audio_text):
    try:
        resp_dict = {}
        new_story_scene_master_response = Story_Scene_Master_Response(story_scene_speaker = new_story_scene_speaker, audio_filename = audio_filename, audio_text = audio_text)
        db.session.add(new_story_scene_master_response)
        db.session.commit()
        resp_dict['status'] = 'success'
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def upload_story_zip(story_zip):
    try:
        resp_dict = {}
        #Temporarily save zip the file to the bucket
        zip_upload_response = save_story_object(story_zip, story_zip.filename, True)
        if zip_upload_response['status'] == 'success':
            zip_url = zip_upload_response['object_url']
            #Open the URL pointing to the zip file
            zip_response = urlopen(zip_url)
            #Read the content to memory
            zip_file_content = ZipFile(BytesIO(zip_response.read()))
            #Loop through each file and save it to the bucket
            for file_name in zip_file_content.namelist():
                if zip_file_content.open(file_name).read():
                    story_object = zip_file_content.open(file_name).read()
                    upload_resp = save_story_object(story_object, file_name, False)
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

def upload_story_json(story_json):
    try:
        resp_dict = {}
        #Read the JSON content to string then load it as JSON object
        story_string = story_json.read().decode('utf-8')
        json_dict = json.loads(story_string)

        #Insert the main story and pass new_story to story_scene
        insert_story_response = insert_story(json_dict['name'], json_dict['description'], json_dict['length'], json_dict['image_filename'], json_dict['difficulty'], json_dict['genre'], json_dict['is_demo'])
        if insert_story_response['status'] == 'success':
            new_story = insert_story_response['new_story']
            #Insert the scene
            for story_scene in json_dict['story_scenes']:
                insert_story_scene_response = insert_story_scene(new_story, story_scene['order'], story_scene['type'], story_scene['next_scene_order'])
                if insert_story_scene_response['status'] == 'success':
                    new_scene = insert_story_scene_response['new_scene'] 
                    #insert the keywords
                    insert_scene_keyword_response = insert_scene_keyword(new_scene, story_scene['scene_keywords'])
                    if insert_scene_keyword_response['status'] == 'success':
                        for speaker in story_scene['story_scene_speakers']:
                            #insert scene speakers
                            insert_story_scene_speaker_response = insert_story_scene_speaker(new_scene, speaker['order'], speaker['image_filename'], speaker['audio_filename'], speaker['audio_text'], speaker['prompt'])
                            if insert_story_scene_speaker_response['status'] == 'success':
                                new_story_scene_speaker = insert_story_scene_speaker_response['new_story_scene_speaker']
                                for master_response in speaker['story_scene_master_responses']:
                                    #insert scene master response
                                    insert_story_scene_master_responses_response = insert_story_scene_master_responses(new_story_scene_speaker, master_response['audio_filename'], master_response['audio_text'])

        resp_dict['status'] = 'success'
        resp_dict['message'] = 'JSON successfully uploaded'

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

        if 'story_json' not in request.files:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No JSON file found'
            return jsonify(resp_dict), 400
        
        upload_zip_response = upload_story_zip(request.files['story_zip'])
        if upload_zip_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = upload_zip_response['message']
            return jsonify(resp_dict), 500

        upload_json_response = upload_story_json(request.files['story_json'])
        if upload_json_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = upload_json_response['message']
            return jsonify(resp_dict), 500
        
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'story content uploaded successfully'
        return jsonify(resp_dict), 201

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

def get_scene(story_id, scene_order):
    try:
        resp_dict = {}
        
        scene = Story_Scene.query.filter(Story_Scene.story_id == story_id, Story_Scene.order == scene_order).first()
        if not scene:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No scene found'
            return resp_dict

        scene_schema = Story_Scene_Schema()
        scene_data = scene_schema.dump(scene).data
        for speaker in scene_data['story_scene_speakers']:
            speaker['audio_filename'] = generate_presigned_url(app.config.get('S3_BUCKET'), app.config.get('S3_CONTENT_DIR')+'/'+speaker['audio_filename'])
            speaker['image_filename'] = generate_presigned_url(app.config.get('S3_BUCKET'), app.config.get('S3_CONTENT_DIR')+'/'+speaker['image_filename'])

        resp_dict['status'] = 'success'
        resp_dict['scene_data'] = scene_data
        
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

@app.route('/start_story', methods=['POST'])
@token_required
def start_story():
    try:
        resp_dict = {}
        story_data = request.get_json()

        if not 'story_uid' in story_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No story in request'
            return jsonify(resp_dict),400

        if not 'user_uid' in story_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user in request'
            return jsonify(resp_dict),400
        
        story = Story.query.filter_by(uid = story_data['story_uid'].strip()).first()
        if not story:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No story found'
            return resp_dict

        user = User.query.filter_by(uid = story_data['user_uid'].strip()).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404
        
        user_story = User_Story.query.filter(User_Story.user_id == user.id, User_Story.story_id == story.id, User_Story.completed == 0).order_by(User_Story.created_at.desc()).first()
        if user_story:
            #If user has incomplete story, send back next scene order & existing user_story_uid
            story_scene_user_response = Story_Scene_User_Response.query.filter_by(user_story_id = user_story.id).order_by(Story_Scene_User_Response.story_scene_speaker_id.desc()).first()
            next_scene_order = story_scene_user_response.story_scene_speaker.story_scene.order + 1
            
            resp_dict['status'] = 'success'
            resp_dict['pending_story'] = True
            resp_dict['next_scene_order'] = next_scene_order
            resp_dict['user_story_uid'] = user_story.uid
            return jsonify(resp_dict), 200
        else:
            #If user does not have a pending story, send back the first scene data & a new user_story_id
            user_story_uid = str(uuid.uuid4())
            new_user_story = User_Story(uid = user_story_uid, user_id = user.id, story_id = story.id, completed = 0)
            db.session.add(new_user_story)
            db.session.commit()
        
            get_scene_response = get_scene(story.id, 1)
            if get_scene_response['status'] == 'success':
                scene_data = get_scene_response['scene_data']
                resp_dict['status'] = 'success'
                resp_dict['pending_story'] = False
                resp_dict['scene_data'] = scene_data
                resp_dict['user_story_uid'] = user_story_uid
                return jsonify(resp_dict), 200
            else:
                resp_dict['status'] = get_scene_response['status']
                resp_dict['message'] = get_scene_response['message']
                return jsonify(resp_dict)

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Get the scene based on the user_story_uid & order
@app.route('/get_story_scene',methods=['GET'])
@token_required
def get_story_scene():
    try:
        resp_dict = {}
        user_story_uid = request.args.get('uid', type=str)
        scene_order = request.args.get('order', 1, type=int)

        #use user_story_uid to get story id to pass into get_scene
        user_story = User_Story.query.filter_by(uid = user_story_uid).first()
        if not user_story:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user story found'
            return jsonify(resp_dict),404

        get_scene_response = get_scene(user_story.story_id, scene_order)
        if get_scene_response['status'] == 'success':
            scene_data = get_scene_response['scene_data']
            resp_dict['status'] = 'success'
            resp_dict['scene'] = scene_data
            return jsonify(resp_dict), 200
        else:
            resp_dict['status'] = get_scene_response['status']
            resp_dict['message'] = get_scene_response['message']
            return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Restart the story
@app.route('/restart_story',methods=['POST'])
@token_required
def restart_story():
    try:
        resp_dict = {}
        story_data = request.get_json()

        if not 'story_uid' in story_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No story in request'
            return jsonify(resp_dict),400

        if not 'user_uid' in story_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user in request'
            return jsonify(resp_dict),400
        
        story = Story.query.filter_by(uid = story_data['story_uid'].strip()).first()
        if not story:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No story found'
            return resp_dict

        user = User.query.filter_by(uid = story_data['user_uid'].strip()).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

        user_story_uid = str(uuid.uuid4())
        new_user_story = User_Story(uid = user_story_uid, user_id = user.id, story_id = story.id, completed = 0)
        db.session.add(new_user_story)
        db.session.commit()
    
        get_scene_response = get_scene(story.id, 1)
        if get_scene_response['status'] == 'success':
            scene_data = get_scene_response['scene_data']
            resp_dict['status'] = 'success'
            resp_dict['scene_data'] = scene_data
            resp_dict['user_story_uid'] = user_story_uid
            return jsonify(resp_dict), 200
        else:
            resp_dict['status'] = get_scene_response['status']
            resp_dict['message'] = get_scene_response['message']
            return jsonify(resp_dict)

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500


#Receive the user_story_uid + user response + next scene order & return next scene
@app.route('/user_response', methods=['POST'])
@token_required
def user_response():
    try:
        resp_dict = {}
     
        if 'user_audio' not in request.files:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No audio file found'
            return jsonify(resp_dict), 400

        user_story_uid = request.form['user_story_uid'].strip()
        story_scene_speaker_id = request.form['story_scene_speaker_id'].strip()
        audio_text = request.form['audio_text'].strip()
        next_scene_order = request.form['next_scene_order'].strip()
        
        user_story = User_Story.query.filter_by(uid = user_story_uid).first()
        if not user_story:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user story found'
            return jsonify(resp_dict),404

        audio_upload_response = save_story_object(request.files['user_audio'], app.config.get('USER_RESPONSE_DIR') + '/' + request.files['user_audio'].filename, False)
        if audio_upload_response['status'] == 'success':
            new_user_response = Story_Scene_User_Response(user_story_id = user_story.id, story_scene_speaker_id = story_scene_speaker_id, audio_filename = request.files['user_audio'].filename, audio_text = audio_text)
            db.session.add(new_user_response)
            db.session.commit()
        else:
            resp_dict['status'] = audio_upload_response['status']
            resp_dict['message'] = audio_upload_response['message']
            return jsonify(resp_dict),500

        get_scene_response = get_scene(user_story.story_id, next_scene_order)
        if get_scene_response['status'] == 'success':
            scene_data = get_scene_response['scene_data']
            resp_dict['status'] = 'success'
            resp_dict['scene'] = scene_data
            return jsonify(resp_dict), 200
        else:
            resp_dict['status'] = get_scene_response['status']
            resp_dict['message'] = get_scene_response['message']
            return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500
