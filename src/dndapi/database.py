import sqlite3
from datetime import datetime
from dndapi import app

DATABASE_LOCATION = '/data/development.db'

def makedb():
    # Connect to the sqlite database. This can be mounted as a dir
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        # Create table
        c.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id               INTEGER  PRIMARY KEY,
            first_name       TEXT NOT NULL,
            last_name        TEXT NOT NULL,
            physical_address TEXT NOT NULL,
            dci_number       TEXT,
            email_address    TEXT );''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id          INTEGER PRIMARY KEY,
            timestamp   TIMESTAMP NOT NULL,
            amount      INTEGER NOT NULL,
            method      TEXT NOT NULL,
            donor_id    INTEGER NOT NULL,
            FOREIGN KEY(donor_id) REFERENCES donors(id)
        );''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id          INTEGER PRIMARY KEY,
            timestamp   TIMESTAMP NOT NULL,
            amount      INTEGER NOT NULL,
            reason      TEXT NOT NULL,
            donor_id    INTEGER NOT NULL,
            FOREIGN KEY(donor_id) REFERENCES donors(id)
        );''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL UNIQUE,
            race        TEXT NOT NULL,
            class       TEXT NOT NULL,
            state       TEXT NOT NULL,
            num_resses  INTEGER DEFAULT 0,
            player_id   INTEGER NOT NULL,
            start_time  TIMESTAMP,
            end_time    TIMESTAMP,
            FOREIGN KEY(player_id) REFERENCES donors(id)
        );''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS dms (
            id         INTEGER PRIMARY KEY,
            name       TEXT NOT NULL,
            team       TEXT NOT NULL,
            numkills   INTEGER DEFAULT 0,
            current    INTEGER default 0
        )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS queue(
            id            INTEGER PRIMARY KEY,
            position      INTEGER NOT NULL,
            character_id  INTEGER NOT NULL,
            FOREIGN KEY(character_id) REFERENCES characters(id)
        )''')
        # commit the changes
        dbconn.commit()



###############################################################################################
# DONOR FUNCTIONS
def get_donor_by_id(donor_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        app.logger.info('before querty')
        c.execute("""
        SELECT
          donors.id,
          donors.first_name,
          donors.last_name,
          donors.physical_address,
          donors.dci_number,
          donors.email_address,
          coalesce(don.amt, 0) as total_donations,
          coalesce(don.amt, 0)-coalesce(pur.pamt, 0) as available_gold
        FROM donors
        LEFT JOIN (SELECT donor_id, sum(amount) as amt FROM donations GROUP BY donor_id) as don ON donors.id = don.donor_id
        LEFT JOIN (SELECT donor_id, sum(amount) as pamt FROM purchases GROUP BY donor_id) as pur ON donors.id = pur.donor_id
        WHERE donors.id = ?""", [donor_id,])
        row = c.fetchone()
        app.logger.info('after fetchone')
        result = {}
        if row:
            app.logger.info('row exists')
            result = {'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'physical_address': row[3],
                    'dci_number': row[4],
                    'email_address': row[5],
                    'total_donations': row[6]/100.0,
                    'available_gold': row[7]/100.0 }
            return result
        else:
            app.logger.info('No rows found')
            return None
        
    
def get_all_donors():   
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""
        select
            donors.id,
            donors.first_name,
            donors.last_name,
            donors.physical_address,
            donors.dci_number,
            donors.email_address,
            coalesce(don.amt, 0) as total_donations,
            coalesce(don.amt, 0)-coalesce(pur.pamt, 0) as available_gold
        FROM donors
        LEFT JOIN (SELECT donor_id, sum(amount) as amt FROM donations GROUP BY donor_id) as don ON donors.id = don.donor_id
        LEFT JOIN (SELECT donor_id, sum(amount) as pamt FROM purchases GROUP BY donor_id) as pur ON donors.id = pur.donor_id;
        """)
        rows = c.fetchall()
        res = [ {'id': row[0],
           'first_name': row[1],
           'last_name': row[2],
           'physical_address': row[3],
           'dci_number': row[4],
           'email_address': row[5],
           'total_donations': row[6]/100.0,
           'available_gold': row[7]/100.0 } for row in rows ]
        return res

# Inserts the donor information into the database
def insert_new_donor(first_name,
                     last_name,
                     physical_address,
                     dci_number,
                     email_address):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""INSERT INTO donors(
                    first_name,
                    last_name,
                    physical_address,
                    dci_number,
                    email_address ) VALUES (?, ?, ?, ?, ?);""", 
            [ first_name, last_name, physical_address, dci_number, email_address ])
        # Return the just inserted object (this now includes the id)
        c.execute("""SELECT * FROM donors WHERE rowid=?;""", (c.lastrowid,))
        row = c.fetchone()
        res = {'id': row[0],
           'first_name': row[1],
           'last_name': row[2],
           'physical_address': row[3],
           'dci_number': row[4],
           'email_address': row[5] }
        dbconn.commit()
        return res


##################################################################################################
### DONATION QUERIES
def get_donation_by_id(donation_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute('SELECT * FROM donations WHERE id=?', (donation_id,) )
        row = c.fetchone()
        if row:
            return { 'id': row[0],
                     'timestamp': row[1],
                     'amount': row[2],
                     'method': row[3],
                     'donor_id': row[4] }
        else:
            return None

def get_donations_for_donor(donor_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""SELECT * FROM donations WHERE donor_id=?;""", (donor_id,))
        rows = c.fetchall()
        res = []
        for row in rows:
            res.append( {'id': row[0],
               'timestamp': row[1],
               'amount': row[2],
               'method': row[3],
               'donor_id': row[4] } )
        return res

def insert_donation(amount, method, donor_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""INSERT INTO donations(amount, timestamp, method, donor_id) values(?,?,?,?)""", 
                  [amount, datetime.now(), method, donor_id])
        c.execute("""SELECT * FROM donations WHERE rowid=?;""", (c.lastrowid,))
        row = c.fetchone()
        res = {'id': row[0],
               'timestamp': row[1],
               'amount': row[2],
               'method': row[3],
               'donor_id': row[4] }
        dbconn.commit()
        return res




#####################################################################################################
## Purchases queries
def insert_purchase(amount, reason, donor_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""INSERT INTO purchases(amount, timestamp, reason, donor_id) values(?,?,?,?)""", 
                  [amount, datetime.now(), reason, donor_id])
        c.execute("""SELECT * FROM purchases WHERE rowid=?;""", (c.lastrowid,))
        row = c.fetchone()
        res = {'id': row[0],
               'timestamp': row[1],
               'amount': row[2],
               'reson': row[3],
               'donor_id': row[4] }
        dbconn.commit()
        return res

def get_purchase_by_id(purchase_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute('SELECT * FROM purchases WHERE id=?', (purchase_id,) )
        row = c.fetchone()
        if row:
            return { 'id': row[0],
                     'timestamp': row[1],
                     'amount': row[2],
                     'reason': row[3],
                     'donor_id': row[4] }
        else:
            return None




###################################################################################################
## Characters queries
###### 
def get_character_by_id(character_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""SELECT * FROM characters WHERE id=?;""", (character_id,))
        row = c.fetchone()
        if row:
            return { 'id': row[0],
                'name': row[1],
                'race': row[2],
                'class': row[3],
                'state': row[4],
                'num_resses': row[5],
                'player_id': row[6],
                'start_time': row[7],
                'end_time': row[8] }
        else:
            return None

def get_characters_for_player(player_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""SELECT * FROM characters WHERE player_id=?;""", (player_id,))
        rows = c.fetchall()
        res = []
        for row in rows:
            res.append( { 'id': row[0],
                'name': row[1],
                'race': row[2],
                'class': row[3],
                'state': row[4],
                'num_resses': row[5],
                'player_id': row[6],
                'start_time': row[7],
                'end_time': row[8] } )
        return res

def insert_character(name, race, clazz, state, player_id):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""INSERT INTO characters(name, race, class, state, player_id) values(?,?,?,?,?)""", 
                  [name, race, clazz, state, player_id])
        c.execute("""SELECT * FROM characters WHERE rowid=?;""", (c.lastrowid,))
        row = c.fetchone()
        res = { 'id': row[0],
                'name': row[1],
                'race': row[2],
                'class': row[3],
                'state': row[4],
                'num_resses': row[5],
                'player_id': row[6],
                'start_time': row[7],
                'end_time': row[8] }
        dbconn.commit()
        return res




#################################################################################################
### DM queries
def get_current_dm():
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        c.execute("""SELECT * FROM dms WHERE current=1;""")
        row = c.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'team': row[2],
                'numkills': row[3],
                'current': row[4]
            }
        else:
            return None

def insert_current_dm(name, team):
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        ## Remove the current one
        c.execute("""UPDATE dms SET current = 0 WHERE current = 1;""")
        ## Add the new one
        c.execute("""INSERT INTO dms(name, team, current) values(?,?,?)""", [name, team, 1])
        dbconn.commit()

def select_dm_teamkills():
    ## This query sums up all of the dmkills based on their team.
    with sqlite3.connect(DATABASE_LOCATION) as dbconn:
        c = dbconn.cursor()
        ## Remove the current one
        c.execute("""SELECT team, sum(numkills) FROM dms GROUP BY team""")
        rows = c.fetchall()
        result = {}
        for row in rows:
            result[row[0]] = row[1]
        return result
