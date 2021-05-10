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
from redis import Redis
from rq import Queue
from rq.job import Job
import time
import os

if not sys.warnoptions:
    import warnings
    for warning in [DeprecationWarning, ResourceWarning]:
        warnings.simplefilter('ignore', warning)

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


#app.default_error_handler = json_error_handler

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
        return False

def createPost(db, data):

    if data is not None:
        keys = data.keys()
    else:
        keys = set()

    missing = missingFields({'username', 'message'}, keys)

    if missing:
        abort(400, missing)

    username = data['username']
    message = data['message']

    try:
        result = query(db, 'INSERT INTO Posts (username, message) VALUES (?, ?);', [username, message])
        response.body = result
        response.status = 200
    except:
        abort(500)

    return response.status

def countHashtags(message):
    r = Redis()
    words = message.split()
    hashtags = {}
    for word in words:
        if word[0] == '#':
            hashtags[word] = hashtags.get(word, 0) + 1

    for tag in hashtags:
        r.zincrby("hashtags", hashtags[tag], tag)
    
    response.status = 200

    return response.status

@get('/timeline/user/<username>/')
def getUserTimeline(username,db):
    myPosts = query(db, 'SELECT message FROM Posts WHERE username = ? ORDER BY id DESC LIMIT 25;', [username])

    return {'posts' : myPosts}

    
       
@get('/timeline/')
def getPublicTimeline(db):

    posts = query(db, 'SELECT username, message FROM Posts ORDER BY id DESC LIMIT 25')

    return {'posts' : posts}

@get('/timeline/home/<username>/')
def getUserTimeline(username, db):

    
    response = requests.get('http://localhost:5000/users/' + username + '/follow/')
    
    data = json.loads(response.text) 
    following = list()

    for x in data['followers']:
        following.append(x.get('Follow'))

    if len(following) == 1:
        posts = query(db, 'SELECT username, message FROM Posts WHERE Username = ? ORDER BY id DESC LIMIT 25;', [following[0]])

    else:
        following_tuple = tuple(following)
        posts = query(db, 'SELECT username, message FROM Posts WHERE Username IN {} ORDER BY id DESC LIMIT 25;'.format(following_tuple))


    return {'Posts': posts}

@post('/timeline/')
def postQueue(db):
    conn = Redis()
    publish = Queue("publish", connection=conn)
    trending = Queue("trending", connection=conn)
    data = request.json

    if data is not None:
        keys = data.keys()
    else:
        keys = set()

    missing = missingFields({'username', 'message'}, keys)

    if missing:
        abort(400, missing)
    
    publish_result = publish.enqueue(createPost(db, data))
    trending_result = trending.enqueue(countHashtags(data['message']))
    publishID = str(publish_result.id)
    trendingID = str(trending_result.id)
    publish_status = Job.fetch(publish_result.id, connection=conn)
    trend_status = Job.fetch(trending_result.id, connection=conn)
    
    if publish_status.is_finished:
        response.status = 200 
    else:
        response.status = 202
    
    return response

@get('/timeline/trending/')
def getHashTags():
    r = Redis()
    try:
        trending = r.zrange("hashtags", 0, 24, True, True)
        response.status = 200
        return {'Trending Topics' : trending}
    except:
        responsebody = {'Error' : 'Unable to retrieve trending topics'}
        response.status = 500

    return response

