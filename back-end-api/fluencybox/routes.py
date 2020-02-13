from flask import request, jsonify, make_response, Response, send_file, url_for
from sqlalchemy import or_
import base64
import os, io
import json
from io import StringIO
from PIL import Image
from fluencybox import app, db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from dateutil.relativedelta import relativedelta
import datetime
from functools import wraps
from fluencybox.models import User, User_Schema, Story, Story_Schema, Story_Scene, Story_Scene_Schema, \
Scene_Keyword, Scene_Keyword_Schema, Story_Scene_Speaker, Story_Scene_Speaker_Schema, Story_Scene_Speaker_Report_Schema, \
Story_Scene_Master_Response, Story_Scene_Master_Response_Schema, User_Story, User_Story_Schema, \
Story_Scene_User_Response, Story_Scene_User_Response_Schema, Report, Report_Schema, \
Report_Images, Report_Images_Schema, Story_Purchase, Story_Purchase_Schema, User_Purchase, User_Purchase_Schema, \
Credit_Cards, Credit_Cards_Schema, Subscriptions, Subscriptions_Schema, Subscription_Contracts, Subscription_Contracts_Schema, \
Current_Subscription_Contracts, Current_Subscription_Contracts_Schema
from fluencybox.S3AssetManager import get_bucket, get_resource, save_avatar, save_story_object, delete_avatar, \
delete_story_object, generate_presigned_url, run_task
from fluencybox.mailer import send_reset_email, send_report_complete_email
from fluencybox.helper import insert_story, insert_story_scene, insert_scene_keyword, insert_story_scene_speaker, \
insert_story_scene_master_responses, validate_user_name, validate_email_address, get_paginated_list, upload_story_zip, \
upload_story_json, get_scene, generate_tokens, generate_public_url, get_paginated_story
from fluencybox.stripe_manager import create_customer, create_payment_token, create_card, create_subscription, get_invoice
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
file_handler = logging.FileHandler('api.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# @app.route('/')
# def index():
#     return jsonify({'Page' : 'Index'})

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

def admin_required(f):
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

            current_user = User.query.filter_by(uid = payload['uid']).first()

            if not current_user.is_admin:
                resp_dict['status'] = 'fail'
                resp_dict['message'] = 'Admin access only'
                return jsonify(resp_dict), 403

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
        
        if user.is_admin == 1:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'Admin access only'
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

        new_user = User(uid = uid, first_name = first_name, last_name = last_name, email_address = email_address, user_name = user_name, password = hashed_password, phone_number = phone_number, refresh_token = refresh_token, is_admin = 0)
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
@app.route('/')
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
        user_uid = request.args.get('uid', type=str)
        
        user = User.query.filter_by(uid = user_uid).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404
        
        subscription = Subscriptions.query.filter_by(user_id = user.id).first()
        if not subscription:
            subscription_status = 'inactive'
        else:
            subscription_status = subscription.status

        story_list = Story.query.paginate(page = page, per_page = per_page)
        paginated_list = get_paginated_story(story_list, subscription_status)
        
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
        story_data['image_url'] = generate_public_url('story_image', story_data['image_filename'])
        
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
        user_uid = request.args.get('uid', type=str)
        
        user = User.query.filter_by(uid = user_uid).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

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
        
        subscription = Subscriptions.query.filter_by(user_id = user.id).first()
        if not subscription:
            subscription_status = 'inactive'
        else:
            subscription_status = subscription.status

        paginated_list = get_paginated_story(story_list, subscription_status)

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
            return jsonify(resp_dict),404

        user = User.query.filter_by(uid = story_data['user_uid'].strip()).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404
        
        #Check if story is demo story
        if not story.is_demo:
            print(story.is_demo)
            #Check if user has an active subscription
            subscription = Subscriptions.query.filter_by(user_id = user.id).first()
            if not subscription:
                subscription_status = 'inactive'
            else:
                subscription_status = subscription.status

            print(subscription_status)
            if subscription_status != 'active':
                resp_dict['status'] = 'fail'
                resp_dict['message'] = 'user subscription is inactive'
                return jsonify(resp_dict),400


        user_story = User_Story.query.filter(User_Story.user_id == user.id, User_Story.story_id == story.id, User_Story.completed == 0).order_by(User_Story.created_at.desc()).first()
        if user_story:
            #If user has incomplete story, send back next scene order & existing user_story_uid
            story_scene_user_response = Story_Scene_User_Response.query.filter_by(user_story_id = user_story.id).order_by(Story_Scene_User_Response.story_scene_speaker_id.desc()).first()
            #To cater for situation where user doesn't submit a response for the first scene
            if story_scene_user_response:
                next_scene_order = story_scene_user_response.story_scene_speaker.story_scene.order + 1
            else:
                next_scene_order = 1

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

        #Rename audio file
        _, audio_ext = request.files['user_audio'].filename.split('.',1)
        audio_uid = str(uuid.uuid4()) + '.' + audio_ext

        audio_upload_response = save_story_object(request.files['user_audio'], app.config.get('USER_RESPONSE_AUDIO_DIR') + '/' + audio_uid, True)
        if audio_upload_response['status'] == 'success':
            new_user_response = Story_Scene_User_Response(user_story_id = user_story.id, story_scene_speaker_id = story_scene_speaker_id, audio_filename = audio_uid, audio_text = audio_text)
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

#Mark the story as complete & trigger SQS
@app.route('/complete_story', methods=['POST'])
@token_required
def complete_story():
    print("stage 0")
    try:
        resp_dict = {}
        story_data = request.get_json()

        if not 'user_story_uid' in story_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user story uid in request'
            return jsonify(resp_dict),400
        
        user_story = User_Story.query.filter_by(uid = story_data['user_story_uid'].strip()).first()
        if not user_story:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user story found'
            return jsonify(resp_dict),404

        user_story.completed = 1
        report_uid = str(uuid.uuid4())
        new_report = Report(uid = report_uid, user_story_id = user_story.id)
        db.session.add(new_report)
        db.session.commit()

        # Trigger task
        report_url = 'http://back-end-withreport-dev.us-west-1.elasticbeanstalk.com' + url_for('taskPayload', uid=report_uid)
        print(report_url)
        run_task(report_url)

        resp_dict['status'] = 'success'
        print('stage 5.5')
        print(resp_dict)
        print(resp_dict['status'])
        return jsonify(resp_dict), 200
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

@app.route('/reports/<uid>/task_payload', methods=['GET'])
def taskPayload(uid):
    print("stage 6")
    try:
        report = Report.query.filter_by(uid=uid).first()
        if not report:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No report found'
            return jsonify(resp_dict), 404

        user_story = User_Story.query.filter_by(id = report.user_story_id).first()
        if not user_story:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user story found'
            return jsonify(resp_dict), 404

        task_payload = {}
        task_payload['s3_bucket'] = app.config.get('S3_BUCKET')
        task_payload['report_uid'] = uid
        task_payload['callback_url'] = url_for('reports', uid = uid, api_key = app.config.get('S3_KEY'), _external=True)
        task_payload['user_story_uid'] = user_story.uid
        
        #Get 'specific_response' scenes for this story
        story_scene = Story_Scene.query.filter(Story_Scene.story_id == user_story.story_id, Story_Scene.type == 'specific_response').all()

        
        story_scene_responses = []
        for scene in story_scene:
            for speaker in scene.story_scene_speakers:
                # To cater for speakers that don't have a master response
                if speaker.story_scene_master_responses.__len__()>0: 
                    data_dict = {}
                    data_dict['story_scene_speaker_id'] = speaker.id
                    for master_response in speaker.story_scene_master_responses:
                        master = {
                            'audio_filename': 'master_response_audio/' + master_response.audio_filename,
                            'audio_text' : master_response.audio_text
                        }
                        data_dict['master'] = master
                    user_response = Story_Scene_User_Response.query.filter(Story_Scene_User_Response.user_story_id == user_story.id, Story_Scene_User_Response.story_scene_speaker_id == speaker.id).first()
                

                    user = {
                        'audio_filename': 'user_response_audio/' + user_response.audio_filename,
                        'story_scene_user_response_id' : user_response.id
                    }
                    data_dict['user'] = user

                    story_scene_responses.append(data_dict)

        task_payload['story_scene_responses'] = story_scene_responses
        print("stage 7")
        print(task_payload)
        return jsonify(task_payload), 200

        #             #To cater for non existent user response
        #             if not user_response:
        #                 print('No User Response for user_story.id = ', user_story.id, ' & story_scene_speaker_id = ', speaker.id)
        #             else:
        #                 user = {'audio_filename': user_response.audio_filename, 'story_scene_user_response_id' : user_response.id}
        #                 data_dict['user'] = user

        #             story_scene_responses.append(data_dict)

        # sqs_payload['story_scene_responses'] = story_scene_responses #json.dumps(story_scene_responses)
        # #Send ECS command to run a task
        
        # #resp_dict['status'] = 'success'
        # resp_dict['sqs_payload'] = sqs_payload
        
        # return jsonify(resp_dict), 200

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#http://127.0.0.1:5000/reports/9c9f4d3c-62b7-4cab-b06b-14a82bd025b1/images?api_key=AKIAUPHFJDPHPRSNXQZ21
@app.route('/reports/<uid>/images', methods=['POST'])
def reports(uid):
    try:
        resp_dict = {}
        request_dict = {}
        api_key = request.args.get('api_key', type=str)

        if api_key == app.config.get('S3_KEY'):
            report_data = request.get_json()

            my_report = Report.query.filter_by(uid = uid).first()
            my_report.score = report_data['score']
            db.session.commit()

            for image_data in report_data['report_images']:
                _, filename = image_data['image_filename'].strip().split('/',1)
                new_report_images = Report_Images(report_id = my_report.id, filename = filename, scene_user_response_id = image_data['story_scene_user_response_id'], image_type = image_data['image_type'].strip())
                db.session.add(new_report_images)
            db.session.commit()
            
            #Send Email
            user_story = User_Story.query.filter_by(uid = report_data['user_story_uid'].strip()).first()
            user = User.query.filter_by(id = user_story.user_id).first()
            story = Story.query.filter_by(id = user_story.story_id).first()
            send_report_complete_email(user, story, uid)
        
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'invalid key'
            return jsonify(resp_dict), 401

        resp_dict['status'] = 'success'
        return jsonify(resp_dict), 200
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Get all reports - paginate using page = 1 and per_page = 10 args in the URL
@app.route('/reports',methods=['GET'])
@token_required
def get_all_reports():
    try:
        resp_dict = {}
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        user_uid = request.args.get('uid', type=str)
        
        user = User.query.filter_by(uid = user_uid).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

        report_list = db.session.query(Report).join(User_Story).filter(User_Story.user_id == user.id, User_Story.completed == 1).order_by(Report.uploaded_at.desc()).paginate(page = page, per_page = per_page)

        paginated_list = get_paginated_list(report_list, 'report')

        if paginated_list['status'] == 'success':
            resp_dict['status'] = 'success'
            resp_dict['reports'] = paginated_list['paginated_list']
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

@app.route('/reports/<uid>',methods=['GET'])
@token_required
def get_single_report(uid):
    try:
        resp_dict = {}
        report_details = {}
        report_images = []
        report = Report.query.filter_by(uid = uid).first()
        
        if not report:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No report found'
            return jsonify(resp_dict),404
        
        report_details['uid'] = report.uid
        report_details['name'] = report.user_story.story.name + " speech report"
        report_details['score'] = report.score
        story_scene_speaker_schema = Story_Scene_Speaker_Report_Schema(many= True)

        for report_image in report.report_images:
            if report_image.image_type == 'stress':
                filename_stress = report_image.filename
                filename_uid = filename_stress.split("_stress.jpg")[0]
                filename_rhythm = filename_uid + "_rhythm.jpg"

                master_response = Story_Scene_Master_Response.query.filter(Story_Scene_Master_Response.story_scene_speaker_id == report_image.story_scene_user_response.story_scene_speaker_id).first()
                story_scene_speakers = Story_Scene_Speaker.query.filter_by(story_scene_id = master_response.story_scene_speaker.story_scene.id).all()
                story_scene_speakers_data = story_scene_speaker_schema.dump(story_scene_speakers).data
                for speaker in story_scene_speakers_data:
                    speaker['audio_filename'] = generate_public_url('speaker_audio', speaker['audio_filename'])
                    
                report_image_url_stress = generate_public_url('report_image', filename_stress)
                report_image_url_rhythm = generate_public_url('report_image', filename_rhythm)

                master_audio_url = generate_public_url('master_audio', master_response.audio_filename)
                user_response_audio_url = generate_public_url('user_audio', report_image.story_scene_user_response.audio_filename)
                
                report_images.append({
                    'master_audio_url' : master_audio_url,
                    'user_response_audio_url' : user_response_audio_url,
                    
                    'user_response_audio_text' : report_image.story_scene_user_response.audio_text,
                    
                    'report_image_type_stress' : report_image.image_type,
                    'report_image_url_stress' : report_image_url_stress, 
                    
                    'report_image_type_rhythm' : 'rhythm',
                    'report_image_url_rhythm' : report_image_url_rhythm, 
                    
                    #New keys added
                    'master_response_text' : master_response.audio_text,
                    'scene_number' : master_response.story_scene_speaker.story_scene.order,
                    'scene_user_response_score' : report_image.scene_user_response_score,
                    'story_scene_speakers' : story_scene_speakers_data 
                    })

        report_details['report_images'] = report_images
        
        resp_dict['status'] = 'success'
        resp_dict['report_details'] = report_details
        
        return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500


#Add User Purchase details
@app.route('/user_purchase',methods=['POST'])
@token_required
def user_purchase():
    try:
        resp_dict = {}
        user_data = request.get_json()
        #Check if all fields are present in JSON request 
        if not 'user_uid' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user uid in request'
            return jsonify(resp_dict),400

        if not 'amount' in user_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No amount in request'
            return jsonify(resp_dict),400

        if not 'stripe_charge_id' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No stripe charge id in request'
            return jsonify(resp_dict),400
        
        if not 'brand' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No brand in request'
            return jsonify(resp_dict),400

        if not 'last_four' in user_data: 
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No credit card digits in request'
            return jsonify(resp_dict),400
        
        user_uid = user_data['user_uid'].strip() 
        amount = user_data['amount']
        stripe_charge_id = user_data['stripe_charge_id'].strip()
        brand = user_data['brand'].strip() 
        last_four = user_data['last_four'].strip() 

        user = User.query.filter_by(uid = user_uid).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

        new_user_purchase = User_Purchase(user_id = user.id, amount = amount, stripe_charge_id = stripe_charge_id, brand = brand, last_four = last_four)
        db.session.add(new_user_purchase)
        db.session.commit()

        resp_dict['status'] = 'success'
        resp_dict['message'] = 'User Purchase data saved'

        return jsonify(resp_dict),201
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Admin Only End points
#Get all F.E users - paginate using page = 1 and per_page = 10 args in the URL - Admin Only
@app.route('/users',methods=['GET'])
@token_required
@admin_required
def get_all_users():
    try:
        resp_dict = {}
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        is_admin = request.args.get('is_admin', 'false', type=str)
        if is_admin == 'true':
            is_admin = 1
        else:
            is_admin = 0
        
        user_list = User.query.filter(User.is_admin == is_admin).paginate(page = page, per_page = per_page)
        
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

#Get a specific admin
@app.route('/users/<uid>/admin',methods=['GET'])
@token_required
@admin_required
def get_admin_user(uid):
    try:
        resp_dict = {}
        user = User.query.filter_by(uid = uid).first()
        
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No admin found'
            return jsonify(resp_dict),404

        if user.is_admin == 0:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'User not admin'
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


@app.route('/upload_story', methods=['POST'])
@token_required
@admin_required
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

        upload_json_response = upload_story_json(request.files['story_json'])
        if upload_json_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = upload_json_response['message']
            return jsonify(resp_dict), 500
        media_dict = upload_json_response['media_dict']

        upload_zip_response = upload_story_zip(request.files['story_zip'], media_dict)
        if upload_zip_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = upload_zip_response['message']
            return jsonify(resp_dict), 500
        
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'story content uploaded successfully'
        return jsonify(resp_dict), 201

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500



@app.route('/subscriptions', methods=['POST'])
#@token_required
def subscription():
    try:
        resp_dict = {}
        sub_data = request.get_json()
        #Check if all fields are present in JSON request 
        if not 'user_uid' in sub_data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user uid in request'
            return jsonify(resp_dict),400
            
        # Uncomment when F.E sends token
        # if not 'payment_token' in sub_data:
        #     resp_dict['status'] = 'fail'
        #     resp_dict['message'] = 'No payment token in request'
        #     return jsonify(resp_dict),400
        # Uncomment when F.E sends token

        user_uid = sub_data['user_uid'].strip() 
        
        # Uncomment when F.E sends token
        # payment_token = sub_data['payment_token']
    
        user = User.query.filter_by(uid = user_uid).first()
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

        create_customer_response = create_customer(user)
        if create_customer_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = create_customer_response['message']
            return jsonify(resp_dict), 500
        customer = create_customer_response['message']
    
        #Temp use - real payment token will be received from F.E - comment this out
        create_payment_token_response = create_payment_token()
        if create_payment_token_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = create_payment_token_response['message']
            return jsonify(resp_dict), 500
        payment_token = create_payment_token_response['message']
        #Temp use - real payment token will be received from F.E - comment this out

        create_card_response = create_card(customer.id, payment_token.id)
        if create_card_response['status'] != 'success':
            resp_dict['status'] = 'fail'
            resp_dict['message'] = create_card_response['message']
            return jsonify(resp_dict), 500
        card = create_card_response['message']

        new_card = Credit_Cards(user_id = user.id, stripe_card_id = card.id, brand = card.brand, last_four = card.last4, exp_month = card.exp_month, exp_year = card.exp_year)
        db.session.add(new_card)

        new_subscription = Subscriptions(user_id = user.id, stripe_customer_id = customer.id, status = 'active')
        db.session.add(new_subscription)

        period_start = datetime.date.today()
        period_end = period_start + relativedelta(months=1)

        new_subscription_contract = Subscription_Contracts(subscription = new_subscription, stripe_plan_id =  app.config.get('HANASU_PLAN_ID'), amount = 999,  credit_card = new_card, period_start = period_start, period_end = period_end)
        db.session.add(new_subscription_contract)

        new_current_subscription_contracts = Current_Subscription_Contracts(subscription = new_subscription, subscription_contract = new_subscription_contract)
        db.session.add(new_current_subscription_contracts)

        create_subscription_response = create_subscription(customer.id, card.id)
        if create_subscription_response['status'] != 'success':
            db.session.rollback()
            resp_dict['status'] = 'fail'
            resp_dict['message'] = create_subscription_response['message']
            return jsonify(resp_dict), 500
        
        subscription = create_subscription_response['message']

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

    try:
        #Update the stripe subscription id
        new_subscription.stripe_subscription_id = subscription.id

        #Update charge id, start/end periods & invoice id
        new_subscription_contract.stripe_invoice_id = subscription.latest_invoice

        #Get the invoice to get the charge id
        get_invoice_response = get_invoice(subscription.latest_invoice)
        if get_invoice_response['status'] == 'success':
            invoice = get_invoice_response['message']
            new_subscription_contract.stripe_charge_id = invoice.charge

        new_subscription_contract.period_start = datetime.datetime.fromtimestamp(int(subscription.current_period_start)).strftime('%Y-%m-%d %H:%M:%S')
        new_subscription_contract.period_end = datetime.datetime.fromtimestamp(int(subscription.current_period_end)).strftime('%Y-%m-%d %H:%M:%S')
        db.session.commit()

        resp_dict['status'] = 'success'
        return jsonify(resp_dict), 201
    except Exception as e:
        resp_dict['status'] = 'success'
        logger.exception('Error occurred: ' + str(e))
        return jsonify(resp_dict), 201

#Get a users cards
@app.route('/users/<uid>/credit_cards',methods=['GET'])
@token_required
def get_user_cards(uid):
    try:
        resp_dict = {}
        user = User.query.filter_by(uid = uid).first()
        
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404

        credit_cards = Credit_Cards.query.filter_by(user_id = user.id).all()

        credit_cards_schema = Credit_Cards_Schema()
        credit_cards_data = credit_cards_schema.dump(credit_cards).data

        resp_dict['status'] = 'success'
        resp_dict['cards'] = credit_cards_data
        
        return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

#Get a users cards
@app.route('/credit_cards',methods=['POST'])
@token_required
def add_credit_card():
    try:
        resp_dict = {}
        data = request.get_json()
        #Check if all fields are present in JSON request 
        if not 'user_uid' in data:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user uid in request'
            return jsonify(resp_dict),400
        user_uid = data['user_uid'].strip() 

        # Uncomment when F.E sends token
        # if not 'payment_token' in sub_data:
        #     resp_dict['status'] = 'fail'
        #     resp_dict['message'] = 'No payment token in request'
        #     return jsonify(resp_dict),400
        # Uncomment when F.E sends token
        
        user = User.query.filter_by(uid = user_uid).first()
        
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


#Delete a users cards
@app.route('/credit_cards/<id>',methods=['DELETE'])
@token_required
def delete_user_card(id):
    try:
        resp_dict = {}
        ## F.E should check if the user has more than 1 card, only then should it be able to send a delee request to the API.
        ## Once the Card ID is received, confirm from database that the user has another card on file
        ##https://stripe.com/docs/api/cards/delete
        card = User.query.filter_by(uid = id).first()
        
        if not card:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No card found'
            return jsonify(resp_dict),404


        resp_dict['status'] = 'success'
        resp_dict['cards'] = 'user_data'
        
        return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500


#Get a users subscriptions
@app.route('/subscriptions/<id>/subscription_contracts',methods=['GET'])
@token_required
def get_user_subscriptions(uid):
    try:
        resp_dict = {}
        #Paginated list of contracts order by period_start DESC

        user = User.query.filter_by(uid = uid).first()
        
        if not user:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = 'No user found'
            return jsonify(resp_dict),404


        users_schema = User_Schema()
        user_data = users_schema.dump(user).data

        resp_dict['status'] = 'success'
        resp_dict['cards'] = user_data
        
        return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500



#Delete a users subscription
@app.route('/subscriptions/<id>',methods=['DELETE'])
@token_required
def delete_subscription(id):
    try:
        resp_dict = {}
        ##https://stripe.com/docs/api/subscriptions/cancel
       
        resp_dict['status'] = 'success'
        resp_dict['cards'] = 'user_data'
        
        return jsonify(resp_dict)
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return jsonify(resp_dict), 500

