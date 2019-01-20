from flask import Flask, render_template, request, redirect, session, flash, json
from flask_cors import CORS, cross_origin
import re
import gspread
from gspread.exceptions import CellNotFound, APIError
from oauth2client.service_account import ServiceAccountCredentials
import socket
import requests
import requests_toolbelt.adapters.appengine
import json
import time
from twilio.rest import Client
import urllib

requests_toolbelt.adapters.appengine.monkeypatch()

app = Flask(__name__)
app.secret_key = '12sdfJHBKBb kdf894423nfmldnJKBKNSFMd'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

account_sid = 'AC107bdb8d0c51fe9b1106818540ebce01'
auth_token = 'f5bdb8d6fbb3d5e8afbfee61b31f30f7'
client = Client(account_sid, auth_token)


def dbcheck(phone, password):
    gc.login()
    try:
        row = UD.find(phone).row
    except CellNotFound:
        row = False
    if row is not False:
        if password == UD.cell(row, 4, value_render_option='FORMULA').value:
            return True
        else:
            return False
    else:
        return False


def makecall(phone, password, calltext):
    if calltext == "call":
        try:
            row = UD.find(phone).row
        except CellNotFound:
            row = False
        if row is not False:
            phonemsg = UD.cell(row, 5, value_render_option='FORMULA').value
            msg = urllib.quote(phonemsg)
            call = client.calls.create(
                url='https://calloutapp-229103.appspot.com/twilio/{}'.format(msg),
                to='+1{}'.format(str(phone)),
                from_='+15172450912'
            )
            return "call made"
        else:
            return "Unable to find that phone number in the database. "
    elif calltext == "text":
        try:
            row = UD.find(phone).row
        except CellNotFound:
            row = False
        if row is not False:
            textmsg = UD.cell(row, 6, value_render_option='FORMULA').value
            texter(phone, textmsg)
            return "text sent"
        else:
            return "Unable to find that phone number in the database."
    else:
        return "There was an error deciding if you wanted to call or text, please try again"


def makecompcall(phone, password, calltext, cstmsg, cstdelay):
    if calltext == "call":
        time.sleep(int(cstdelay))
        msg = urllib.quote(cstmsg)
        call = client.calls.create(
            url='https://calloutapp-229103.appspot.com/twilio/{}'.format(msg),
            to='+1{}'.format(str(phone)),
            from_='+15172450912'
        )
        return "call made"
    elif calltext == "text":
        time.sleep(int(cstdelay))
        texter(phone, cstmsg)
        return "text sent"
    else:
        return "There was an error deciding if you wanted to call or text, please try again"


def texter(phone, msg):
    message = client.messages.create(
        body="{}".format(str(msg)),
        from_='+15172450912',
        to='{}'.format(str(phone)))


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('calloutapp-229103.json', scope)

gc = gspread.authorize(credentials)

UD = gc.open_by_key('1PdQvaR-qiPLL2zYpMNw-XVg4zWUtjYcOO8fDb0nlah4').worksheet('Users')


@app.route('/')
def landing():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        phone = request.form.get('phone')
        password = request.form.get('password')
        # check for phone in database and it it exists check if password matches
        account = dbcheck(phone, password)
        if account:  # if account exists is True, else False
            session["phone"] = phone
            session["password"] = password
            return redirect("dashboard")
        else:
            return render_template("login.html", error="Incorrect username or password<br>")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if name is not None and email is not None and phone is not None and password is not None and password2 is not None:
            if password == password2:
                emailregex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
                if emailregex.match(email) is not None:
                    nameregex = re.compile(r"^[A-Za-z' ,.-]+$")
                    if nameregex.match(name) is not None:
                        phoneregex = re.compile(r"^[0-9]{10}$")
                        if phoneregex.match(phone) is not None:
                            passwordregex = re.compile(r'^[A-Za-z0-9!@#$%_=+.?-]{8,}$')
                            if passwordregex.match(password) is not None:
                                gc.login()
                                try:
                                    row = UD.find(phone).row
                                except CellNotFound:
                                    row = False
                                if row is False:
                                    gc.login()
                                    try:
                                        row2 = UD.find(email).row
                                    except CellNotFound:
                                        row2 = False
                                    if row2 is False:
                                        new_user = [name, phone, email, password]
                                        UD.append_row(new_user, value_input_option='RAW')
                                        session['phone'] = phone
                                        session['password'] = password
                                        return redirect("dashboard")
                                    else:
                                        return render_template("signup.html", error="That email is already taken<br>")
                                else:
                                    return render_template("signup.html", error="That phone number is already taken<br>")
                            else:
                                return render_template("signup.html", error="Your password includes characters not allowed or is not at least 8 characters<br>")
                        else:
                            return render_template("signup.html", error="Your phone includes characters not allowed, type it using only numbers<br>")
                    else:
                        return render_template("signup.html", error="Your name includes characters not allowed<br>")
                else:
                    return render_template("signup.html", error="Your email appears to be invalid<br>")
            else:
                return render_template("signup.html", error="Your passwords don't match<br>")
        else:
            return render_template("signup.html", error="None of your fields can be blank<br>")


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == "GET":
        if 'phone' in session and 'password' in session:
            phone = session['phone']
            password = session['password']
            if dbcheck(phone, password):
                return render_template("dashboard.html", phone=phone, password=password)
            else:
                return redirect("login")
        else:
            return redirect("login")
    elif request.method == "POST":
        return render_template("dashboard.html")


@app.route('/call', methods=['POST'])
def call():
    if request.method == "POST":
        if 'phone' in session and 'password' in session:
            phone = session['phone']
            password = session['password']
            if dbcheck(phone, password):
                dict = request.json
                try:
                    calltext = dict['calltext']
                except:
                    return "The call the the server was missing data. Please try logging out and back in again"
                try:
                    cstmsg = dict['cstmsg']
                    cstdelay = dict['cstdelay']
                except:
                    cstmsg = False
                    cstdelay = False
                if phone and password and calltext:
                    if cstmsg and cstdelay:
                        response = makecompcall(phone, password, calltext, cstmsg, cstdelay)
                        return response
                    else:
                        response = makecall(phone, password, calltext)
                        return response
            else:
                return 'There was an error logging you in. Please log out and try again.'
        else:
            dict = request.json
            try:
                phone = dict['phone']
                password = dict['password']
                calltext = dict['calltext']
            except:
                return "The call the the server was missing data. Please try logging out and back in again"
            try:
                cstmsg = dict['cstmsg']
                cstdelay = dict['cstdelay']
            except:
                cstmsg = False
                cstdelay = False
            if phone and password and calltext:
                if cstmsg and cstdelay:
                    if dbcheck(phone, password):
                        response = makecompcall(phone, password, calltext, cstmsg, cstdelay)
                        return response
                    else:
                        return "Incorrect phone number or password"
                else:
                    if dbcheck(phone, password):
                        response = makecall(phone, password, calltext)
                        return response
                    else:
                        return "Incorrect phone number or password"
            else:
                return "Error parsing json"
    else:
        return "Somehow it is and isnt Post"


@app.route('/twilio/<msg>', methods=['POST', 'GET'])
@cross_origin()
def callpage(msg):
    return render_template('twilio.xml', message=urllib.unquote(msg))


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/faq')
def faq():
    return render_template("faq.html")


if __name__ == '__main__':
    app.run()
