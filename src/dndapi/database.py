from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os

dbuser = os.environ['DBUSER']
dbpass = os.environ['DBPASS']
dbhost = os.environ['DBHOST']
dbtable = os.environ['DBTABLE']

# Connect to the database
engine = create_engine(
  'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4'%(dbuser, dbpass, dbhost, dbtable),
  echo=True)


# Define the mappings
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Donor(Base):
    __tablename__ = 'donors'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    physical_address = Column(String(200), nullable=False)
    dci_number = Column(String(30))
    email_address = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return "<Donor(id='%s', first_name='%s', last_name='%s', email_address='%s', physical_address='%s', dci_number='%s')>" % (
                self.id, self.first_name, self.last_name, self.email_address, self.physical_address, self.dci_number)
    

class Donation(Base):
    __tablename__ = 'donations'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    amount = Column(Numeric(13,2), nullable=False)
    method = Column(String(30), nullable=False)
    reason = Column(String(10), nullable=False)
    donor_id = Column(Integer, ForeignKey('donors.id'), nullable=False)

    def __repr__(self):
        return "<Donation(timestamp='%s', amount='%s', method='%s', reason='%s')>" % (
                self.timestamp, self.amount, self.method, self.reason)


class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)
    race = Column(String(20), nullable=False)
    char_class = Column(String(20), nullable=False)
    state = Column(String(10), nullable=False)
    starttime = Column(DateTime)
    deathtime = Column(DateTime)
    num_resses = Column(Integer, nullable=False, default=0)
    queue_pos = Column(Integer)
    donor_id = Column(Integer, ForeignKey('donors.id'), nullable=False)

    def __repr__(self):
        return "<Character(name='%s', race='%s', class='%s', state='%s', starttime='%s', deathtime='%s', num_resses='%s', queue_pos='%s')>" % (
            self.name, self.race, self.char_class, self.state, self.starttime, self.deathtime, self.num_resses, queue_pos)


class Dm(Base):
    __tablename__ = 'dms'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    team = Column(String(30), nullable=False)
    num_kills = Column(Integer, nullable=False, default=0)
    state = Column(String(20))

    def __repr__(self):
        return "<Dm(id='%s', name='%s', team='%s', num_kills='%s', state='%s')>" % (
                self.id, self.name, self.team, self.num_kills, self.state)

# create the schema
Base.metadata.create_all(engine)

