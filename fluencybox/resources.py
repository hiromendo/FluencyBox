import boto3
from botocore.exceptions import NoCredentialsError
from fluencybox.config import S3_BUCKET, S3_KEY, S3_SECRET

def _get_s3_resource():
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
    else:
        return boto3.resource('s3')

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
    s3_resource = _get_s3_resource()
    bucket = S3_BUCKET
    return s3_resource.Bucket(bucket)

def get_objects():
    s3_resource = _get_s3_resource()
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()
    return summaries

def get_client():
    s3 = boto3.client('s3', aws_access_key_id=S3_KEY,
                      aws_secret_access_key=S3_SECRET)
    return s3