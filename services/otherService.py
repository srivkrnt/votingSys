from random import randint
import requests
from services import bridge, aadharService
db = bridge.get_db()
Voter = bridge.get_voter_model()
Message = bridge.get_message_model()
Votes = bridge.get_votes_model()
Log = bridge.get_log_model()

def build_voter_data(voter):
    if voter is None:
        return voter

    data = {}
    data['id'] = voter.id
    data['name'] = voter.name
    data['username'] = voter.username
    data['password'] = voter.password
    data['age'] = voter.age
    data['phone'] = voter.phone
    data['aadharNumber'] = voter.aadharNumber
    data['address'] = voter.address

    return data

def build_message_data(message):
    if message is None:
        return message
    data = {}
    data['id'] = message.id
    data['phone'] = message.phone
    data['otp'] = message.otp

    return data

def get_voter_by_aadhar(aadharNumber):
    voter = Voter.query.filter_by(aadharNumber=aadharNumber).first()
    voter = build_voter_data(voter)
    return voter

def get_voter_by_phone(phone):
    voter = Voter.query.filter_by(phone=phone).first()
    voter = build_voter_data(voter)
    return voter

def get_voter_by_username(username):
    voter = Voter.query.filter_by(username=username).first()
    voter = build_voter_data(voter)
    return voter

def get_phone_by_username(username):
    voter = Voter.query.filter_by(username=username).first()
    voter = build_voter_data(voter)
    return voter['phone']

def get_aadhar_by_username(username):
    voter = Voter.query.filter_by(username=username).first()
    voter = build_voter_data(voter)
    return voter['aadharNumber']

def check_voted_status(username):
    aadharNumber = get_aadhar_by_username(username)

    voted = Votes.query.filter_by(aadharNumber=aadharNumber).first()
    if voted is None:
        return False
    else:
        return True

def save_vote_data(username):
    aadharNumber = get_aadhar_by_username(username)
    vote = Votes(aadharNumber)
    db.session.add(vote)
    db.session.commit()

def verify_login_details(username, password):
    voter = get_voter_by_username(username)
    if voter is None:
        return False

    if voter['password'] == password:
        return True
    return False

def add_candidate_vote(candidate):
    vote = Log(candidate)
    db.session.add(vote)
    db.session.commit()

def add_voter(voter_details):
    try:
        voter_by_aadhar = get_voter_by_aadhar(voter_details['aadharNumber'])
        voter_by_phone = get_voter_by_phone(voter_details['phone'])
        voter_by_username = get_voter_by_username(voter_details['username'])
        aadharStatus = aadharService.verify_aadhar_number(voter_details['aadharNumber'])

        if aadharStatus == False or len(voter_details['phone']) != 10:
            return {"failure" : "Details wrong", "status_code" : 401}
        if voter_by_aadhar is None and voter_by_username is None and voter_by_phone is None and aadharStatus == True:
            voter = Voter(voter_details["name"], voter_details['username'], voter_details['password'],voter_details['age'], voter_details["phone"], voter_details["aadharNumber"], voter_details["address"])
            db.session.add(voter)
            db.session.commit()

            return {"success" : "Voter Added", "status_code" : 200}
        else:
            return {"failure" : "Voter Already exist", "status_code" : 400}
    except:
        return {"failure" : "Voter Adding failed, check details", "status_code" : 401}

def save_otp_to_message_log(phone, otp):
    message = Message(phone, otp)

    db.session.add(message)
    db.session.commit()

def send_otp(username):
    phone = get_phone_by_username(username)
    otp = str(randint(10000, 99999))
    authkey = "269393AWPvsvkheywo5c9a45a6"
    message = "Otp for casting vote is - %s " % (otp)

    endPoint = "https://api.msg91.com/api/sendhttp.php?route=4&sender=VOTEIN&message=%s&country=91&mobiles=%s&authkey=%s" % (message, phone, authkey)
    response = requests.get(endPoint)
    if response.status_code == 200:
        save_otp_to_message_log(phone, otp)
        return {"success" : "OTP sent"}
    else:
        return {"failure" : "check Details"}

def send_message(username, message):
    phone = get_phone_by_username(username)
    authkey = "269393AWPvsvkheywo5c9a45a6"
    endPoint = "https://api.msg91.com/api/sendhttp.php?route=4&sender=VOTEIN&message=%s&country=91&mobiles=%s&authkey=%s" % (message, phone, authkey)
    response = requests.get(endPoint)
    if response.status_code == 200:
        return {"success" : "Message sent"},200
    else:
        return {"failure" : "Something went wrong"},400

def verify_otp(otp, phone):
    last_record = Message.query.filter_by(phone=phone).all()
    if len(last_record) == 0:
        return False
    last_record = last_record[-1]
    message = build_message_data(last_record)
    if message['otp'] == otp:
        return True
    else:
        return False

def get_result():
    result = []
    candidates = ["1", "2", "3", "4"]
    for candidate in candidates:
        rows = Log.query.filter_by(candidate = candidate).all()
        result.append((candidate, len(rows)))

    return result
