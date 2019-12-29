from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'SECRET'
db = SQLAlchemy(app)

def set():
    return (app, db)

class Voter(db.Model):
    """ Voter model for storing voters """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(10))
    aadharNumber = db.Column(db.String(12))
    address = db.Column(db.String(200))
    voted = db.Column(db.Boolean)

    def __init__(self, name, username, password, age, phone, aadharNumber, address):
        self.name = name
        self.username = username
        self.password = password
        self.age = age
        self.phone = phone
        self.aadharNumber = aadharNumber
        self.address = address
        self.voted = False

class Message(db.Model):
    """ For Internal use of Phone Service """
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    phone = db.Column(db.String(10))
    otp = db.Column(db.String(10))

    def __init__(self, phone, otp):
        self.phone = phone
        self.otp = otp

class Votes(db.Model):
    """ For maintaining votes """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aadharNumber = db.Column(db.String(12))

    def __init__(self, aadharNumber):
        self.aadharNumber = aadharNumber

class Log(db.Model):
    """ For maintaining votes """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidate = db.Column(db.String(12))

    def __init__(self, candidate):
        self.candidate = candidate

def getClasses():
    return (Voter, Message, Votes, Log)
def getDb():
    return db
