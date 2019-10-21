import uuid
import re
import base64
import os, io
import json
from fluencybox import app, db
from fluencybox.models import User, User_Schema, Story, Story_Schema, Story_Scene, Story_Scene_Schema, \
Scene_Keyword, Scene_Keyword_Schema, Story_Scene_Speaker, Story_Scene_Speaker_Schema, \
Story_Scene_Master_Response, Story_Scene_Master_Response_Schema, User_Story, User_Story_Schema, \
Story_Scene_User_Response, Story_Scene_User_Response_Schema, Report, Report_Schema, \
Report_Images, Report_Images_Schema, Story_Purchase, Story_Purchase_Schema, User_Purchase, User_Purchase_Schema
from fluencybox.S3AssetManager import get_bucket, get_resource, save_avatar, save_story_object, \
delete_avatar, delete_story_object, generate_presigned_url, generate_public_url
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from io import StringIO
import jwt
import datetime

#common method to generate tokens
def generate_tokens(uid):
    tokens = {}
    access_token = jwt.encode({'uid' : uid, 'token_type' : 'access_token' , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
    refresh_token = jwt.encode({'uid' : uid, 'token_type' : 'refresh_token' , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['REFRESH_TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
	
    tokens['access_token'] = access_token.decode('UTF-8')
    tokens['refresh_token'] = refresh_token.decode('UTF-8')

    return tokens


def validate_user_name(user_name):
    regex = '^[A-Za-z0-9_-]+$'
    if(re.search(regex,user_name)): 
        return True
    else:
        return False

def validate_email_address(email_address):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email_address)): 
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
                image_url = generate_public_url('story_image', story.image_filename)
                output.append({
                'uid' : story.uid, 
                'name' : story.name,
                'description' : story.description,
                'length' : story.length,
                'image_url' : image_url,
                'difficulty' : story.difficulty,
                'genre' : story.genre,
                'is_demo': story.is_demo
                })
        elif object_type == 'report':
            for report in page_object.items:
                output.append({
                    'uid' : report.uid,
                    'name' : report.user_story.story.name + " speech report",
                    'uploaded_at' : report.uploaded_at,
                    'score' : report.score,
                    'genre' : report.user_story.story.genre
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


def upload_story_zip(story_zip, media_dict):
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
                    if file_name in media_dict:
                        uid_filename = media_dict[file_name]
                        upload_resp = save_story_object(story_object, uid_filename, True)
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
        media_dict = {}
        #Read the JSON content to string then load it as JSON object
        story_string = story_json.read().decode('utf-8')
        json_dict = json.loads(story_string)

        #Insert the main story and pass new_story to story_scene
        _, image_ext = json_dict['image_filename'].split('.',1)
        image_uid = str(uuid.uuid4()) + '.' + image_ext
        media_dict[json_dict['image_filename']] = app.config.get('STORY_IMAGES_DIR') + '/' + image_uid

        insert_story_response = insert_story(json_dict['name'], json_dict['description'], json_dict['length'], image_uid, json_dict['difficulty'], json_dict['genre'], json_dict['is_demo'])
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
                            if speaker['image_filename'] in media_dict:
                                _, image_uid = media_dict[speaker['image_filename']].split('/', 1)
                            else:
                                _, image_ext = speaker['image_filename'].split('.',1)
                                image_uid = str(uuid.uuid4()) + '.' + image_ext
                                media_dict[speaker['image_filename']] = app.config.get('SPEAKER_IMAGES_DIR') + '/' + image_uid
                            
                            if speaker['audio_filename'] in media_dict:
                                _, audio_uid = media_dict[speaker['audio_filename']].split('/', 1)
                            else:
                                _, audio_ext = speaker['audio_filename'].split('.',1)
                                audio_uid = str(uuid.uuid4()) + '.' + audio_ext
                                media_dict[speaker['audio_filename']] = app.config.get('SPEAKER_AUDIO_DIR') + '/' + audio_uid

                            insert_story_scene_speaker_response = insert_story_scene_speaker(new_scene, speaker['order'], image_uid, audio_uid, speaker['audio_text'], speaker['prompt'])
                            if insert_story_scene_speaker_response['status'] == 'success':
                                new_story_scene_speaker = insert_story_scene_speaker_response['new_story_scene_speaker']
                                
                                for master_response in speaker['story_scene_master_responses']:
                                    #insert scene master response
                                    if master_response['audio_filename'] in media_dict:
                                        _, audio_uid = media_dict[master_response['audio_filename']].split('/', 1)
                                    else:
                                        _, audio_ext = master_response['audio_filename'].split('.',1)
                                        audio_uid = str(uuid.uuid4()) + '.' + audio_ext
                                        media_dict[master_response['audio_filename']] = app.config.get('MASTER_RESPONSE_AUDIO_DIR') + '/' + audio_uid
                                    
                                    insert_story_scene_master_responses_response = insert_story_scene_master_responses(new_story_scene_speaker, audio_uid, master_response['audio_text'])
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'JSON successfully uploaded'
        resp_dict['media_dict'] = media_dict
        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

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
            speaker['audio_url'] = generate_public_url('speaker_audio', speaker['audio_filename'])
            speaker['image_url'] = generate_public_url('speaker_image', speaker['image_filename'])

        resp_dict['status'] = 'success'
        resp_dict['scene_data'] = scene_data
        
        return resp_dict
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict
