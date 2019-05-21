import boto3

# get the service resource
s3 = boto3.client('s3',
                       aws_access_key_id='key',
                       aws_secret_access_key='key',
                       aws_session_token='key')

bucket_name = 'cse355sample'
object_name = 'big_file'

local_file = 'E:/다운로드/부산행_NonDRM_[FHD].mp4'




#create_mu_response = s3.create_multipart_upload(Bucket = bucket_name,Key = object_name)

create_multipart_upload_response = s3.create_multipart_upload(Bucket=bucket_name, Key=object_name)

upload_id = create_multipart_upload_response['UploadId']

part_size = 10*1024*1024
parts=[]


# upload parts
with open(local_file, 'rb') as f:
    part_number = 1
    while True:
        data = f.read(part_size)
        if not len(data):
            break
        upload_part_response = s3.upload_part(Bucket=bucket_name,
                                              Key=object_name,
                                              PartNumber=part_number,
                                              UploadId=upload_id, Body=data)
        parts.append({
            'PartNumber': part_number,
            'ETag': upload_part_response['ETag']
        })
        part_number += 1

multipart_upload = {'Parts': parts}

# abort multipart upload
# s3.abort_multipart_upload(Bucket=bucket_name, Key=object_name, UploadId=upload_id)

# complete multipart upload
s3.complete_multipart_upload(Bucket=bucket_name, Key=object_name, UploadId=upload_id, MultipartUpload=multipart_upload)

