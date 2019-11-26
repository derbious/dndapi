import os

ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin')
STAFF_PASS = os.getenv('STAFF_PASS', 'staff')

# Define a User obj. needed for authentication
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    def __str__(self):
        return "User(id='%s',username='%s')"%(self.id, self.username)

# Define the users, and userid table
USERS = [
  User(1, 'admin', os.getenv('ADMIN_PASS', 'admin')),
  User(2, 'staff', os.getenv('STAFF_PASS', 'staff')) 
]
USERID_TABLE = {u.id: u for u in USERS}

def authenticate(username, password):
    for u in USERS:
        if username == u.username and password == u.password:
            return u
    return None

def identity(payload):
    user_id = payload['identity']
    return USERID_TABLE.get(user_id, None)
