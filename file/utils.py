import boto3
from .aws import key, secret_key, session_token
s3 = boto3.client('s3',
                       aws_access_key_id=key,
                       aws_secret_access_key=secret_key,
                       aws_session_token =session_token)
import math
bucket = 'khusb-sample'

def get_upload_url(user, path):
    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': bucket,
            'Key': user+path,
        }
    )
    return url


def get_download_url(user, path):
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': user+path,
        }
    )
    return url


def create_multipart_upload(user, path):
    result = s3.create_multipart_upload(Bucket=bucket, Key=user+path)
    return result['UploadId']


def get_upload_part_url(user, path,  size, UploadId, chunksize):
    urls = {}
    for i in range(1, math.ceil(int(size)/int(chunksize))+1):
        url = s3.generate_presigned_url(
            ClientMethod='upload_part',
            Params={
                'Bucket': bucket,
                'Key': user+path,
                'PartNumber': i,
                'UploadId': UploadId,
            }
        )
        urls[str(i)] = url
    return urls


def complete_multipart_upload(user, path, UploadId, MultipartUpload):
    s3.complete_multipart_upload(Bucket=bucket, Key=user+path, UploadId=UploadId, MultipartUpload=MultipartUpload)


def delete_object(user, path):
    objects_to_delete = s3.list_objects(Bucket=bucket, Prefix=user+path)
    delete_keys = {'Objects': []}
    delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
    s3.delete_objects(Bucket=bucket, Delete=delete_keys)


def copy_object(user, sourcepath, destpath):
    copy_source = {'Bucket': bucket, 'Key': user+sourcepath}
    s3.copy_object(Bucket=bucket, CopySource=copy_source, Key=destpath)


def move_object(user, sourcepath, destpath):
    copy_source = {'Bucket': bucket, 'Key': user+sourcepath}
    s3.copy_object(Bucket=bucket, CopySource=copy_source, Key=destpath)
    s3.delete_object(Bucket=bucket, Key=sourcepath)
