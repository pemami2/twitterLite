#!/usr/bin/python

import json
from bottle import request, response
from bottle import post, get, put, delete
import bottle
from bottle.ext import sqlite

app = bottle.Bottle()
plugin = bottle.ext.sqlite.Plugin(dbfile ='/db/Users.db')

app.install(plugin)

def json_error_handler(res):
    if res.content_type == 'application/json':
        return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
        res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({'error': res.body})


app.default_error_handler = json_error_handler

def query(db, sql, args=(), one=False):
    cur = db.execute(sql, args)
    rv = [dict((cur.description[idx][0], value)
          for idx, value in enumerate(row))
          for row in cur.fetchall()]
    cur.close()

    return (rv[0] if rv else None) if one else rv


def execute(db, sql, args=()):
    cur = db.execute(sql, args)
    id = cur.lastrowid
    cur.close()

    return id

@post('/users/')
def createUser():
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
        row = query(db, 'INSERT INTO Users (username, email, password) VALUES (?, ?, ?);', [username, password, email])

        if not row:
            abort(404)

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
    
    return "hit"

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000) 
    
