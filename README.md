# dndonations Web App

## Description
This is a basic python(flask) CRUD app that uses sqlite. It serves up the API endpoints
and the static html that runs our dndonations logging system

## Development
### Requirements
To get the development environment up and running you need docker installed.

### Testing workflow
1. Do some editing
2. Rebuild the container with the command `docker build . -t dndapi` 
3. Run the newly built container: `docker run -it -p 8080:8080 dndapi` This binds to port 8080 to serve up the web frontend
4. Point your browser to `http://localhost:8080/` to see your changes in action.

The terminal output should show python logging info, and the browser developer console shows the javascript related debug info.

### Notable files
* `__init__.py`: This kicks off the webserver.
* `auth.py`: This handles the authentication. we are using JWT to do the API auth
* `database.py`: This is the database controller. it contains all of the sqlite3 code
* `endpoints/*.py`: These run all of the api endpoints. They are separated out by function

## Techical Details
### DB Schema
```
+------------------------------+
|Donors                        |
+------------------------------+
|id               INTEGER pkey +<---+-+-+
|first_name       TEXT         |    | | |
|last_name        TEXT         |    | | |
|physical_address TEXT         |    | | |
|dci_number       TEXT         |    | | |
+------------------------------+    | | |
                                    | | |
+-----------------------+           | | |
|Donations              |           | | |
+-----------------------+           | | |
|id        INTEGER pkey |           | | |
|timestamp TIMESTAMP    |           | | |
|amount    INTEGER      |           | | |
|method    TEXT         |           | | |
|donor_id  INTEGER      +-----------+ | |
+-----------------------+             | |
                                      | |
+------------------------+            | |
|Purchases               |            | |
+------------------------+            | |
|id        INTEGER pkey  |            | |
|timestamp TIMESTAMP     |            | |
|amount    INTEGER       |            | |
|reason    TEXT          |            | |
|donor_id  INTEGER       +------------+ |
+------------------------+              |
                                        |
+-------------------------+             |
|Characters               |             |
+-------------------------+             |
|id          INTEGER pkey |             |
|name        TEXT UNIQUE  |             |
|race        TEXT         |             |
|class       TEXT         |             |
|state       TEXT         |             |
|num_resses  INTEGER      |             |
|player_id   INTEGER      +-------------+
|start_time  TIMESTAMP    |
|end_time    TIMESTAMP    |
+-------------------------+
```
