#!/usr/bin/python
# script to delete messages table
import boto3



# Get the service resource.
dynamodb = boto3.resource('dynamodb',
    endpoint_url='http://localhost:8000',   
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey')

table = dynamodb.Table('Messages')

response = table.delete()
print(response)