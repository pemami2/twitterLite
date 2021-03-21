#!/usr/bin/python

import sys
import textwrap
import logging.config
import sqlite3
import requests
import bottle
import json
from bottle import get, post, error, abort, request, response, HTTPResponse
from bottle.ext import sqlite

app = bottle.default_app()
plugin = bottle.ext.sqlite.Plugin(dbfile ='db/Posts.db')

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


@get('/timeline/usertimeline/<username>/')
def getUserTimeline(username,db):

    myPosts = query(db, 'SELECT message FROM Posts WHERE username = ? LIMIT 25;', [username])

    return {'posts' : myPosts}

    
       
@get('/timeline/usertimeline/')
def getPublicTimeline(db):

    posts = query(db, 'SELECT message FROM Posts LIMIT 25')

    return {'posts' : posts}

@get('/timeline/hometimeline/<username>/')
def getUserTimeline(username, db):

    try:
        response = requests.get('http://127.0.0.1:8000/users/' + username + '/follow/')
        print(response.text)
    except:
        abort(500, 'User service unavailable')

    data = json.loads(response.text) 
    following = list()

    for x in data['followers']:
        following.append(x.get('Follow'))

    following_tuple = tuple(following)

    try:
        posts = query(db, 'SELECT message FROM Posts WHERE Username IN {} LIMIT 25;'.format(following_tuple))
    except:
        abort(500)

    return {'Posts': posts}

@post('/timeline/')
def user_creation(db):
    '''Handles name creation'''

    data = request.json

    if not data or not {'username', 'message'} <= data.keys():
        abort(400, 'Missing fields')

    username = data['username']  
    message = data['message']

    try: 
        result = query(db, 'INSERT INTO Posts (username, message) VALUES (:username, :message);', {'username': username, 'message': message})
        response.body = result
        response.status = 200
    except:
        abort(500)

    return response.status  


if __name__ == '__main__':
    bottle.run(host = '127.0.0.1', port = 8001) 
    
