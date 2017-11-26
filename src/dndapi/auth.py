import os
from werkzeug.security import safe_str_cmp

# Define a User obj. needed for authentication
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    def __str__(self):
        return "User(id='%s')" % self.id

# pull from ENV variables
users = [
    User(1, 'admin', os.environ['ADMIN_PASSWORD']),
    User(2, 'staff', os.environ['STAFF_PASSWORD']),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)
