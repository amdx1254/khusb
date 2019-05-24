import boto3
import requests
from .aws import *
s3 = boto3.client('s3',
                       aws_access_key_idw=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)

bucket = 'khusb-sample'

