#!/usr/bin/python

import json
import bottle
from bottle import get, post, delete, error, abort, request, response, HTTPResponse
from bottle.ext import sqlite

app = bottle.default_app()
plugin = bottle.ext.sqlite.Plugin(dbfile ='db/Users.db')

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

def missingFields(required, posted):
    if not required <= posted:
        return f'Missing fields: {required - posted}'
    
    else:
        return false

@post('/users/')
def createUser(db):
    '''Handles name creation'''

    data = request.json
    missing = missingFields({'username', 'password', 'email'}, data.keys())

    if missing:
        abort(400, missing)

    username = data['username']  
    password = data['password']
    email = data['email']

    try:
        result = query(db, 'INSERT INTO Users (username, email, password) VALUES (?, ?, ?);', [username, email, password])
    except:
        abort(500)

    response.status = "200 OK"

    return response.status  

@get('/users/checkPassword/<username>/')
def checkPassword(username, db):

    data = request.json
    missing = missingFields({ 'password'}, data.keys())

    if missing:
        abort(400, missing)

    password = data['password']

    try:
        db_pass = query(db, 'SELECT password FROM Users WHERE username = ?;', [username], one=True) 
    except:
        abort(500)

    if db_pass['Password'] == password:
        response.status = 200
    else:
        response.status = 400
        response.body = "Incorrect Password" 
    
    return response


@post('/users/<username>/follow/')
def addFollower(username, db):
    
    data = request.json
    missing = missingFields({'usernameToFollow'}, data.keys())

    if missing:
        abort(400, missing)

    usernameToFollow = data['usernameToFollow']
    try:
        result = query(db, 'INSERT INTO Following (username, follow) VALUES ( ?, ? );', [username, usernameToFollow])
        response.body = result
        response.status = 200
    except:
        abort(500)


    return response

    
       
@delete('/users/<username>/follow/')
def removeFollower(username, db):

    data = request.json
    missing = missingFields({'usernameToUnfollow'}, data.keys())

    if missing:
        abort(400, missing)

    usernameToUnfollow = data['usernameToUnfollow']  
    result = query(db, 'DELETE FROM Following WHERE username = :username AND follow = :follow;', {'username': username, 'follow': usernameToUnfollow}, one = True)
    response.body = result
    response.status = 200

    return response.status 


@get('/users/<username>/follow/')
def getFollowers(username, db):
    
    row = query(db, 'SELECT follow FROM Following WHERE username = ?;', [username])

    return {'followers' : row}

if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8000) 
    
