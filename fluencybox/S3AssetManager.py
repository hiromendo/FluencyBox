from flask import jsonify
import secrets
import os, io
import boto3
from fluencybox import app
from botocore.exceptions import NoCredentialsError
from fluencybox.config import S3_BUCKET, S3_KEY, S3_SECRET
import mimetypes

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


def save_avatar(my_avatar):
    try:
        resp_dict = {}
        my_bucket = get_bucket()
        s3 = get_resource()
        #Create random file name
        hex_name = secrets.token_hex(8)
        _, obj_ext = os.path.splitext(my_avatar.filename)
        obj_fn = hex_name + obj_ext
        mime_type = mimetypes.types_map[obj_ext]

        #set directory, object and content type of the object
        my_bucket.Object(app.config.get('S3_AVATAR_DIR') + '/' + obj_fn).put(Body=my_avatar, ContentType=mime_type)
        #set access permissions
        object_acl = s3.ObjectAcl(app.config.get('S3_BUCKET'), app.config.get('S3_AVATAR_DIR') + '/' + obj_fn)
        response = object_acl.put(ACL='public-read')
        #get full URL to the object
        obj_url = app.config.get('S3_URL') + app.config.get('S3_AVATAR_DIR') + '/' + obj_fn

        resp_dict['status'] = 'success'
        resp_dict['obj_url'] = obj_url
        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict

def save_story_object(my_object):
    try:
        resp_dict = {}
        my_bucket = get_bucket()
        s3 = get_resource()
        
        my_bucket.Object(app.config.get('S3_CONTENT_DIR') + '/' + my_object.filename).put(Body=my_object)
        obj_fn = my_object.filename
        obj_url = app.config.get('S3_URL') + app.config.get('S3_CONTENT_DIR') + '/' + obj_fn

        resp_dict['status'] = 'success'
        resp_dict['obj_url'] = obj_url
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
        file_name = app.config.get('S3_CONTENT_DIR') + '/' + file_name
        my_bucket.Object(file_name).delete()
        
        resp_dict['status'] = 'success'
        resp_dict['message'] = 'successfully deleted'
        return resp_dict

    except Exception as e:
        resp_dict['status'] = 'fail'
        resp_dict['message'] = str(e)
        return resp_dict
