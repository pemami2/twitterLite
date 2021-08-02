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

    if missing:
        abort(400, missing)

    To = data['to']  
    From = data['from']
    Message = data['message'] 
    QuickReplies = (data.get('quickReplies'))
    Time = data['time'] = int(time.time())

    if QuickReplies is None:
        QuickReplies = []
    elif not isinstance(QuickReplies, list):
        abort(400, "Incorrect quick replies format")

    QR = {'L': []}

    for r in QuickReplies:
        QR['L'].append({'S' : str(r)})

    try:
        table.put_item(
            Item={
                "To": To,
                "Time_From": str(Time) + From,
                'From' : From,
                'Time' : Time,
                'Message': Message,
                'QuickReplies': QR,
            }
        )
    except:
        return "database error"

    return {'success': data}



@post('/messages/<ID>/reply/')
def replyToDirectMessage(ID):

    key = ID.split("_")
    data = request.json
    missing = missingFields({'message'}, data.keys())

    if missing:
        abort(400, missing)
    
    # quick reply
    if isinstance(data['message'], int):
        reply = {'N' : str(data['message'])}
    else:
        reply = {'S' : data['message']}


    table.update_item(
        Key={
            'To': key[0],
            'Time_From': key[1]
        },
        UpdateExpression='SET Reply = list_append(if_not_exists(Reply, :empty_list), :val1)',
        ExpressionAttributeValues={
            ':val1': [reply], ':empty_list': []
        }
    )

    return {'success': [{'messageID': ID}, {'reply': reply}]}


@get('/messages/<username>/')
def listDirectMessagesFor(username):
    try:
        response = table.query(
            KeyConditionExpression=Key('To').eq(username)
        )
    except:
        abort(500, "Internal Server Error")
        
    items = response['Items']

    for x in items:
        del x['Time_From']
        del x['To']

    return {'response' : items}



@get('/messages/<ID>/reply/')
def listRepliesTo(ID):
    key = ID.split("_")

    try:
        response = table.get_item(
            Key={
                'To': key[0],
                'Time_From': key[1]
            }
        )
    except:
        abort(500, "Internal Server Error")

    replies = response['Item']['Reply']
    data = []

    for i in range(len(replies)):
        reply = replies[i]

        if 'N' in reply.keys():
            QR = int(reply['N'])
            qRep = response['Item']['QuickReplies']['L']

            if QR < len(qRep):
                data.append( qRep[int(reply['N'])])
            else:
                abort(400, "quickReply does not exist")

        elif 'S' in reply.keys():
            data.append(reply['S'])

        else: 
            abort(500, "Server Error")


    return {'response' : data}


# if __name__ == '__main__':
#     bottle.run(host = 'localhost', port = 5000) 