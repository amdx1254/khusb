"""
코드가 잘 실행되는지 파이썬에서 확인할 때 사용한 코드입니다.
"""

import boto3
import os
from boto3.s3.transfer import TransferConfig, S3Transfer
import time
import sys
import progressbar


s3 = boto3.client('s3',
                  aws_access_key_id='key',
                  aws_secret_access_key='access_key',
                  aws_session_token = 'token')



def download_file( key ):
    s3 = boto3.client('s3',
                      aws_access_key_id='key',
                      aws_secret_access_key='access_key',
                      aws_session_token = 'token')


    try:
        print ("Downloading file:", key)

        tc = boto3.s3.transfer.TransferConfig()
        t = boto3.s3.transfer.S3Transfer( client=s3,config=tc)

        t.download_file( 'cse335-khusb', key,filename,
                       callback = download_progress)


    except Exception as e:
        print ("Error uploading: %s" % ( e ))

def download_progress(chunk):
    up_progress.update(up_progress.currval + chunk)


key = 'mp9/7.zip'
bucket_name = 'cse335-khusb'
filename = os.path.dirname(__file__)+'\\enw\\77.zip'

statinfo = s3.head_object(Bucket=bucket_name, Key=key)['ContentLength']
print(statinfo)
up_progress = progressbar.progressbar.ProgressBar(maxval=statinfo)

up_progress.start()

t = time.time()
download_file(key)
print(time.time()-t)
up_progress.finish()
