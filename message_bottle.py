import sys
import textwrap
import logging.config
import bottle
from bottle import get, post, delete, error, abort, request, response, HTTPResponse
import boto3
import time
import json
from boto3.dynamodb.conditions import Key, Attr


app = bottle.default_app()

    
dynamodb = boto3.resource('dynamodb',
    endpoint_url='http://localhost:8000',   
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey')

# print('hello')
# print(list(dynamodb.tables.all()))
# print(dynamodb.Table("Messages"))

table = dynamodb.Table('Messages')

def missingFields(required, posted):
    if not required <= posted:
        return f'Missing fields: {required - posted}'
    
    else:
        return False

def json_error_handler(res):
    if res.content_type == 'application/json':
        return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
        res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({'error': res.body})


@post('/messages/')
def sendDirectMessage():
    data = request.json
    missing = missingFields({'to', 'from', 'message'}, data.keys())
    print(list(dynamodb.tables.all()))
    print(table)

    if missing:
        abort(400, missing)

    To = data['to']  
    From = data['from']
    Message = data['message'] 
    QuickReplies = data.get('quickReplies')
    Time = int(time.time())

    try:
        table.put_item(
            Item={
                "To": To,
                "Time_From": str(Time) + From,
                'From' : From,
                'Time' : Time,
                'Message': {
                    'S' : Message
                },
                'QuickReplies': {
                    'SS' : QuickReplies
                },
                'Reply': {
                    'L' : []
                }
            }
        )
    except:
        return "database error"

    return 'success'



@post('/messages/<ID>/reply/')
def replyToDirectMessage(ID):

    key = ID.split("_")
    print(key[0])
    print(key[1])
    data = request.json
    missing = missingFields({'message'}, data.keys())

    if missing:
        abort(400, missing)
    
    # quick reply
    if isinstance(data['message'], int):
        response = table.get_item(
            Key={
                'To': key[0],
                'Time_From': key[1]
            }
        )
        replies = response['Item'].get('QuickReplies')
        reply = replies[data['message']]
    else:
        reply = data['message']


    table.update_item(
        Key={
            'To': key[0],
            'Time_From': key[1]
        },
        UpdateExpression='ADD Reply :val1',
        ExpressionAttributeValues={
            ':val1': {reply}
        }
    )

    return 'success'


@get('/messages/<username>/')
def listDirectMessagesFor(username):
    
    response = table.query(
        KeyConditionExpression=Key('To').eq(username)
    )
    items = response['Items']
    for x in items:
        if x.get('Reply') is not None:
            del x['Reply']

    return {'response' : items}



@get('/messages/<ID>/reply/')
def listRepliesTo(ID):
    key = ID.split("_")

    response = table.get_item(
        Key={
            'To': key[0],
            'Time_From': key[1]
        }
    )
    items = list(response['Item'].get('Reply'))

    return {'response' : items}


if __name__ == '__main__':
    bottle.run(host = 'localhost', port = 5000) 