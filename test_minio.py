import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url='https://2b63-156-146-34-246.ngrok-free.app ',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})
)

try:
    response = s3.list_buckets()
    print("Buckets:", response['Buckets'])
except Exception as e:
    print("Ошибка доступа:", e)