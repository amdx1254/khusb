import boto3



# get the service resource
s3 = boto3.resource('s3',
                       aws_access_key_id='key',
                       aws_secret_access_key='key',
                       aws_session_token='key')


s3.create_bucket(Bucket='cse355sample')
