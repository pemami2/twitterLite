#!/usr/bin/python

import boto3



# Get the service resource.
dynamodb = boto3.resource('dynamodb',
    endpoint_url='http://localhost:8000',   
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey')

# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName='Messages',
    KeySchema=[
        {
            'AttributeName': 'To',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'Time_From',
            'KeyType': 'RANGE'
        },

    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'To',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'Time_From',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until the table exists.
table.meta.client.get_waiter('table_exists').wait(TableName='Messages')
# Print out some data about the table.
print(table.item_count)