import boto3

# get the service resource

s3 = boto3.client('s3',
                       endpoint_url = 'https://s3.amazonaws.com',
                       aws_access_key_id='key',
                       aws_secret_access_key='key',
                       aws_session_token='key')


def upload(s3,bucket, obj, local_file_path):
    s3.upload_file(local_file_path, bucket, obj)


#upload
bucket_name = 'cse355sample'
object_name = '1kb.txt'
local_file_path_u = 'C:/Users/julia/1kb.txt'



#create folder
object_name = 'sample-forder/'

#s3.put_object(Bucket=bucket_name, Key=object_name)

object_name = 'sample-forder/1kb.txt'

# 파일 업로드
s3.upload_file(local_file_path_u, bucket_name, object_name)


