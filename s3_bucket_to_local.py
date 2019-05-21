import boto3

# get the service resource
s3 = boto3.client('s3',
                       aws_access_key_id='key',
                       aws_secret_access_key='key',
                       aws_session_token='key')


def download(s3,bucket, obj, local_file_path):
    s3.download_file(bucket, obj, local_file_path)

  
#s3.download_file(Bucket, Key, Filename, ExtraArgs=None, Callback=None, Config=None)


# download
bucket_name = 'cse355sample'
object_name = '1kb.txt'
local_file_path = 'E:/경희대학교/2019_1/클라우드 컴퓨팅/최종샘플/down1kb.txt'



# 파일 다운로드
download(s3, bucket_name, object_name, local_file_path)
