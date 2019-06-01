"""
필요한 부분만 정리한 코드입니다.
"""

import boto3
import os
from boto3.s3.transfer import TransferConfig, S3Transfer





key = 'multipart_files/filename.txt'
bucket_name = 'cse335-khusb'
filename = os.path.dirname(__file__)+'\\filename.txt'


def download_file(bucket, key,filename):
    s3 = boto3.client('s3',
                      aws_access_key_id='key',
                      aws_secret_access_key='access_key',
                      aws_session_token = 'token')



    tc = boto3.s3.transfer.TransferConfig()
    t = boto3.s3.transfer.S3Transfer(client=s3,config=tc)

    t.download_file(bucket, key, filename)



download_file(bucket_name, key, filename)
