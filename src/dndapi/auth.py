import os

# Define a User obj. needed for authentication
class User(object):
    def __init__(self, id, username):
        self.id = id
        self.username = username
    
    def __str__(self):
        return "User(id='%s',username='%s')"%(self.id, self.username)

def authenticate(username, password):
    #TODO fix this
    if username == 'admin':
        return User(1,'admin')
    else:
        return None

def identity(payload):
    return User(1, 'admin')
