from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from config import Config
from services import aadharService,otherService
import json

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'SECRET'
db = SQLAlchemy(app)

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

@app.route('/verify/aadhar/<aadhar_number>')
def verifyAadharNumber(aadhar_number):
    status = aadharService.verify_aadhar_number(str(aadhar_number))
    if status:
        return {"Aadhar Number" : "OK"}, 200
    return {"Aadhar Number" : "Invalid"}, 400

@app.route('/add/voter', methods=['POST'])
def addVoter():
    voter_details = {}
    voter_details['name'] = request.form['name']
    voter_details['username'] = request.form['username']
    voter_details['password'] = request.form['password']
    voter_details['age'] = request.form['age']
    voter_details['phone'] = request.form['phone']
    voter_details['aadharNumber'] = request.form['aadharNumber']
    voter_details['address'] = request.form['address']

    status = otherService.add_voter(voter_details)
    if status['status_code'] == 200:
        return render_template('index.html', alert_message = "Voter Registration Successfull", code = 1)
    elif status['status_code'] == 400:
        return render_template('index.html', alert_message = "Already Registered", code = 2)
    else:
        return render_template('register.html', alert_message = "Wrong Details", code = 1)

@app.route('/castvote')
def castvote():
    alreadyVoted = otherService.check_voted_status(session['username'])
    if session['voted'] == False and not alreadyVoted:
        sendOtp()
        return render_template('castvote.html', voted = session['voted'], alreadyVoted = False)
    else:
        return render_template('castvote.html', voted = session['voted'], alreadyVoted = alreadyVoted)

@app.route('/send/otp')
def sendOtp():
    return otherService.send_otp(session['username'])

@app.route('/verify/otp', methods = ['POST'])
def verifyOtp():
    otp = request.form['otp']
    candidate = request.form['optradio']

    phone = otherService.get_phone_by_username(session['username'])
    status = otherService.verify_otp(otp, phone)

    if status:
        session['voted'] = True
        otherService.save_vote_data(session['username'])
        otherService.add_candidate_vote(candidate)
        otherService.send_message(session['username'], "You have voted Successfully")

        return render_template('index.html', alert_message="Vote Success", code = 1)
    else:
        return render_template('castvote.html', voted = session['voted'], alreadyVoted = False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/login-check', methods = ['POST'])
def checkLogin():
    voter_details = {}
    username = request.form['username']
    password = request.form['password']
    verified = otherService.verify_login_details(username, password)
    if verified:
        session['logged_in'] = True
        session['username'] = username
        session['voted'] = False
        return render_template('index.html', username=username)
    else:
        return render_template('login.html', failed = True)

@app.route('/result')
def result():
    result = otherService.get_result()
    return render_template('result.html', result = result)

@app.route('/profile')
def profile():
    return render_template('profile.html')
    
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template('index.html')

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=8080,debug=True)
