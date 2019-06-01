"""
파이썬에서 잘 실행되는지 확인할 때 사용한 코드입니다.
"""


import boto3
import os
from boto3.s3.transfer import TransferConfig, S3Transfer
import time
import sys
import threading

import progressbar

def upload_file( filename ):
    s3 = boto3.client('s3',
                      aws_access_key_id='key',
                      aws_secret_access_key='access_key',
                      aws_session_token = 'token')


    try:
        print ("Uploading file:", filename)

        tc = boto3.s3.transfer.TransferConfig()
        t = boto3.s3.transfer.S3Transfer( client=s3,config=tc)

        t.upload_file( filename,'cse335-khusb', 'mp9/앨범.zip',
                       callback = upload_progress)


    except Exception as e:
        print ("Error uploading: %s" % ( e ))

def upload_progress(chunk):
    up_progress.update(up_progress.currval + chunk)



bucket_name = 'cse335-khusb'
filename = os.path.dirname(__file__)+'\\앨범.zip'

statinfo = os.stat('앨범.zip')
up_progress = progressbar.progressbar.ProgressBar(maxval=statinfo.st_size)

up_progress.start()

upload_file(filename)

up_progress.finish()
