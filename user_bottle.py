#!/usr/bin/python

import json
from bottle import request, response
from bottle import post, get, put, delete
import bottle
from bottle.ext import sqlite



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
        password=data['password']
        email=data['email']
        response.status = "200 OK"
    except:
        #response.headers['Content-Type'] = 'application/json'
        #print("hi")
        response.status = "400 invalid"
    finally:
        return response.status  

@get('/users/checkPassword/<username>/<password>/')
def checkPassword(username,password):

    
    if "select * username" != password:
        response.status = "400 Invalid" 

    else:
    # return 200 Success
        response.status = "200 Success"
        #response.headers['Content-Type'] = 'application/json'
    return response.status


@put('/users/follower')
def addFollower():
    try:
        # parse input data
        try:
            data = request.json()
        except:
            raise ValueError
        if data is None:
            raise ValueError
        username=data['username']
        usernameToFollow=data['usernametofollow']
        response.status = "200 OK"


    except:
        response.status = "400 INVALID"


    return response.status

    
       
@delete('/users/follower/<username>')
def deletefollower():
    try:
        # parse input data
        try:
            data = request.json()
        except:
            raise ValueError
        if data is None:
            raise ValueError
        usernameToFollow=data['usernametounfollow']
        response.status = 200
    except:
        response.status = 400

    return response.status 


@get('/users/<username>/follower')
def getFollowers(username):
    
    return sql_data

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000) 
    
