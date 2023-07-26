from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
import json
from datetime import datetime


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

config = {
  "apiKey": "AIzaSyBsoZVuaYaOVlsMmcCFbFt1MHcKiA-2itc",
  "authDomain": "cs-miniproject.firebaseapp.com",
  "projectId": "cs-miniproject",
  "storageBucket": "cs-miniproject.appspot.com",
  "messagingSenderId": "535974079899",
  "appId": "1:535974079899:web:a1a7c8f3e06278850c053e",
  "measurementId": "G-M3RZ372TVY",
  "databaseURL": "https://cs-miniproject-default-rtdb.europe-west1.firebasedatabase.app/"
}


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


def get_current_time():
    current_datetime = str(datetime.now())
    current_datetime = current_datetime.split(".")[0]
    return current_datetime


@app.route('/', methods = ['GET', 'POST'])
def welcome():
    return render_template("welcome.html")


@app.route('/explore', methods = ['GET', 'POST'])
def explore():
    try:
        uid = login_session['user']['localId']
        user = db.child("Users").child(uid).get().val()
        inspo = db.child("Explore").get().val()
        if request.method == "POST":
            new_qoute = request.form['qoute']
            inspo = inspo['qoutes'].append(new_qoute)
            db.child("Explore").update(inspo)
        return render_template("explore.html", dict = user, ex = inspo)
    except:
        return render_template("error.html")


@app.route('/add', methods=['GET', 'POST'])
def add():
    date = get_current_time()
    try:
        uid = login_session['user']['localId']
        user = db.child("Users").child(uid).get().val()
        journal = db.child("Journal").child(uid).get().val()
        if request.method == 'POST':
            entry = request.form['entry']
            journal[date] = entry
            db.child('Journal').child(uid).set(journal)
        return render_template("add.html", dict=user, journal=journal)
    except Exception as e:
        print(e)
        return render_template("error.html")


@app.route('/home', methods = ['GET', 'POST'])
def home():
    try:
        uid = login_session['user']['localId']
        user = db.child("Users").child(uid).get().val()
        return render_template("home.html", dict = user)
    except:
        return render_template("error.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
   error = ""
   if request.method == 'POST':
       email = request.form['email']
       password = request.form['password']
       try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            return redirect(url_for('home'))
       except:
           error = "Authentication failed"
   return render_template("login.html", error = error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
   error = ""
   if request.method == 'POST':
       email = request.form['email']
       password = request.form['password']
       full_name = request.form['name']
       username = request.form['username']
       bio = request.form['bio']
       try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            user = {"username":username, "name":full_name, "email":email, "bio":bio, "password":password}
            db.child("Users").child(UID).set(user)
            return redirect(url_for('home'))
       except:
           error = "Authentication failed"
   return render_template("signup.html", error = error)


@app.route('/signout', methods=['GET', 'POST'])
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('welcome'))

#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)