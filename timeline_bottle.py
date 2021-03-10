#!/usr/bin/python

import json
from bottle import request, response
from bottle import post, get, put, delete
import bottle




@get('/timeline/usertimeline/<username>/')
def getUserTimeline(username):

    list_obj=[]

    response.headers['Content-Type'] = 'application/json'
    return json.dump({'timeline':str(list_obj)})


    
       
@get('/timeline/usertimeline/')
def getPublicTimeline():
    user_obj=[]
    list_obj=[]

    response.headers['Content-Type'] = 'application/json'
    return json.dump({'timeline':str(user_obj)})

@get('/timeline/hometimeline/<username>/')
def getUserTimeline(username):

    list_obj=[]

    response.headers['Content-Type'] = 'application/json'
    return json.dump({'timeline':str(list_obj)})


    

@post('/users/')
def user_creation():
    '''Handles name creation'''
    try:
        # parse input data
        try:
            data = request.json()
        except:
            raise ValueError
        if data is None:
            raise ValueError
        username=data['username']  
        text=data['text']
        response.status = "200 OK"
    except:
        response.status = "400 invalid"
    finally:
        return response.status  

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8001) 
    
