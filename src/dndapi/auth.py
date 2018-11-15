import os
import bcrypt
from dndapi import datastore_client

# Define a User obj. needed for authentication
class User(object):
    def __init__(self, id, username):
        self.id = id
        self.username = username
    
    def __str__(self):
        return "User(id='%s',username='%s')"%(self.id, self.username)

def authenticate(username, password):
    query = datastore_client.query(kind='User')
    query.add_filter('username', '=', username)
    users = list(query.fetch())
    if len(users) == 1:
        u = users[0]
        if bcrypt.checkpw(password, u['password']):
            return User(u.id, u['username'])

def identity(payload):
    user_id = payload['identity']
    uk = datastore_client.key('User', user_id)
    user = datastore_client.get(uk)
    if user:
        return User(user_id, user['username'])
