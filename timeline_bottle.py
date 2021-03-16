#!/usr/bin/python

import sys
import textwrap
import logging.config
import sqlite3

import bottle
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
    # list_obj=[]

    # response.headers['Content-Type'] = 'application/json'
    # return json.dump({'timeline':str(list_obj)})
    return {'posts' : myPosts}

    
       
@get('/timeline/usertimeline/')
def getPublicTimeline():
    # user_obj=[]
    # list_obj=[]

    # response.headers['Content-Type'] = 'application/json'
    # return json.dump({'timeline':str(user_obj)})
    return "timeline"

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
    
