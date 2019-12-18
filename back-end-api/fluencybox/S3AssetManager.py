from flask import jsonify
import secrets
import os, io
import boto3
from fluencybox import app
from botocore.exceptions import NoCredentialsError
from fluencybox.config import S3_BUCKET, S3_KEY, S3_SECRET, S3_REGION
import mimetypes
import json

def get_resource():
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
    else:
        return boto3.resource('s3')
        
def get_bucket():
    s3_resource = get_resource()
    bucket = S3_BUCKET
    return s3_resource.Bucket(bucket)

def get_objects():
    s3_resource = get_resource()
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()
    return summaries

def get_client():
    s3 = boto3.client('s3', aws_access_key_id=S3_KEY,
                      aws_secret_access_key=S3_SECRET)
    return s3

def save_s3_object(object_dir, body, content_type, is_public = False):
    try:
        resp_dict = {}
        object_url = ''
        my_bucket = get_bucket()

        if is_public:
            upload_response = my_bucket.Object(object_dir).put(Body = body, ContentType = content_type, ACL='public-read') #set directory, object, content type & public access of the object
            if upload_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                object_url = app.config.get('S3_URL') + object_dir #get full URL to the object
        else:
            upload_response = my_bucket.Object(object_dir).put(Body = body, ContentType = content_type) #set directory, object and content type of the object
        
        if upload_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp_dict['status'] = 'success'
            resp_dict['object_url'] = object_url
            return resp_dict
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = upload_response['ResponseMetadata']['HTTPStatusCode']
            return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict
    
def save_avatar(my_avatar):
    try:
        resp_dict = {}
        #Create random file name
        hex_name = secrets.token_hex(20)
        _, obj_ext = os.path.splitext(my_avatar.filename)
        obj_fn = hex_name + obj_ext
        mime_type = mimetypes.types_map[obj_ext]

        object_dir = app.config.get('S3_AVATAR_DIR') + '/' + obj_fn
        object_url = save_s3_object(object_dir, my_avatar, mime_type, True)

        if object_url['status'] == 'success':
            resp_dict['status'] = 'success'
            avatar_url = object_url['object_url']
            resp_dict['object_url'] = avatar_url
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = object_url['message']
            return resp_dict

        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def save_story_object(my_object, object_filename, is_public = False):
    try:
        resp_dict = {}
        _, obj_ext = os.path.splitext(object_filename) 
        mime_type = mimetypes.types_map[obj_ext]
        object_url = save_s3_object(object_filename, my_object, mime_type, is_public)
        if object_url['status'] == 'success':
            resp_dict['status'] = 'success'
            story_object_url = object_url['object_url']
            resp_dict['object_url'] = story_object_url
            return resp_dict
        else:
            resp_dict['status'] = 'fail'
            resp_dict['message'] = object_url['message']
            return resp_dict
        
    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def delete_avatar(my_avatar):
    try:
        resp_dict = {}
        my_bucket = get_bucket()
        file_name = my_avatar.split('/')[-1]
        file_name = app.config.get('S3_AVATAR_DIR') + '/' + file_name
        default_image = app.config.get('S3_AVATAR_DIR') + '/' + app.config.get('DEFAULT_IMAGE')
        if file_name != default_image:
            my_bucket.Object(file_name).delete()
        
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'successfully deleted'
        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def delete_story_object(my_object_key):
    try:
        resp_dict = {}
        my_bucket = get_bucket()
        file_name = my_object_key.split('/')[-1]
        my_bucket.Object(file_name).delete()
        
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'successfully deleted'
        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def generate_presigned_url(bucket, key):
    resp_dict = {}
    s3_client = get_client()
    try:
        expiry = int(app.config['SIGNED_URL_EXPIRY'])
        if expiry < 1:
            expiry = 300
    except Exception as e:
        expiry = 300

    url = s3_client.generate_presigned_url(ClientMethod = 'get_object', Params = {'Bucket': bucket, 'Key': key}, ExpiresIn = expiry)
    return url

def generate_public_url(object_type, object_name):
    if object_type == 'story_image':
        object_dir = app.config.get('STORY_IMAGES_DIR')
    elif object_type == 'speaker_image':
        object_dir = app.config.get('SPEAKER_IMAGES_DIR')
    elif object_type == 'speaker_audio':
        object_dir = app.config.get('SPEAKER_AUDIO_DIR')
    elif object_type == 'master_audio':
        object_dir = app.config.get('MASTER_RESPONSE_AUDIO_DIR')
    elif object_type == 'user_audio':
        object_dir = app.config.get('USER_RESPONSE_AUDIO_DIR')
    elif object_type == 'report_image':
        object_dir = app.config.get('REPORT_IMAGES_DIR')

    public_url = app.config.get('S3_URL') + object_dir + '/' + object_name
    return public_url


def get_ecs_client():
    return boto3.client('ecs', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET, region_name=S3_REGION)

def run_task(report_url):
    print("stage 1")
    try:
        ecs_client = get_ecs_client()
        print("stage 2")
        response = ecs_client.run_task(
            cluster='generate-report-images',
            taskDefinition='generate-report-images',
            overrides={
                'containerOverrides': [
                    {
                        'name': 'generate-report-images',
                        'command': [
                            report_url
                        ]
                    },
                ]
            },
            count=1,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        'subnet-85758be3',
                        'subnet-3fd4de64'
                    ],
                    'securityGroups': [
                        'sg-6faa9d13',
                    ],
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
        print("stage 3")
        print(response)
        print(response['failures'])
        if len(response['failures']) > 0:
            print("stage 4")
            print('Failed to run task for report_url {}. Failures {}' % (report_url, response['failures']))
            return false
        print("stage 5")
        return True
    except Exception as e:
        print(str(e))
        return False
