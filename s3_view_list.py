import boto3

# get the service resource
s3 = boto3.client('s3',
                       aws_access_key_id='key',
                       aws_secret_access_key='key',
                       aws_session_token='key')


bucket_name = 'cse355sample'


#파일 목록 조회
max_keys = 300
response = s3.list_objects(Bucket=bucket_name, MaxKeys = max_keys)
print("list all in the bucket")

while True:
    print('IsTruncated=%r' % response.get('IsTruncated'))
    print('Marker=%s' % response.get('Marker'))
    print('NextMarker=%s' % response.get('NextMarker'))

    print('Object List')
    for content in response.get('Contents'):
        print(' Name=%s, Size=%d, Owner=%s' % \
              (content.get('Key'), content.get('Size'), content.get('Owner').get('ID')))

    if response.get('IsTruncated'):
        response = s3.list_objects(Bucket=bucket_name, MaxKeys=max_keys,
                                   Marker=response.get('NextMarker'))
    else:
        break

# top level folders and files in the bucket
delimiter = '/'
max_keys = 300

response = s3.list_objects(Bucket=bucket_name, Delimiter=delimiter, MaxKeys=max_keys)

print('top level folders and files in the bucket')

while True:
    print('IsTruncated=%r' % response.get('IsTruncated'))
    print('Marker=%s' % response.get('Marker'))
    print('NextMarker=%s' % response.get('NextMarker'))

    print('Folder List')
    for folder in response.get('CommonPrefixes'):
        print(' Name=%s' % folder.get('Prefix'))

    print('File List')
    for content in response.get('Contents'):
        print(' Name=%s, Size=%d, Owner=%s' % \
              (content.get('Key'), content.get('Size'), content.get('Owner').get('ID')))

    if response.get('IsTruncated'):
        response = s3.list_objects(Bucket=bucket_name, Delimiter=delimiter, MaxKeys=max_keys,
                                   Marker=response.get('NextMarker'))
    else:
        break

