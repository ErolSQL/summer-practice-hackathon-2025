from flask import Flask, url_for, render_template, jsonify, session, request
import smtplib
from models import db, User, OTP
import random
import os
import string
from datetime import datetime, timedelta
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gitgud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def generate_otp():
    return ''.join(random.choices(string.digits, k=8))

db.init_app(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def send_email(to_email, code):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    from_email = 'erolnvm@gmail.com'
    password = 'yiaw hctz ezxw gkbg'

    subject = 'Your verification code'
    body = f'Your code is: {code}'

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, message)


@app.route('/request-otp', methods=['POST'])
def request_otp():
    email = request.json.get('email')
    code = generate_otp()

    OTP.query.filter_by(email=email).delete()

    otp_entry = OTP(email=email, code=code, created_at=datetime.utcnow())
    db.session.add(otp_entry)
    db.session.commit()

    send_email(email, code)
    
    return jsonify({'message': 'OTP sent to your email'})



@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.json.get('email')
    code = request.json.get('code')

    otp_entry = OTP.query.filter_by(email=email, code=code).first()

    if not otp_entry:
        return jsonify({'error': 'Invalid code'}), 400

    if datetime.utcnow() - otp_entry.created_at > timedelta(minutes=1):
        return jsonify({'error': 'Code expired'}), 400


    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.id

    return jsonify({'message': 'Logged in successfully'})

# ---------------------------------------------- PAGINI ----------------------------------------------


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template('register.html')







# ---------------------------------------------- PAGINI ----------------------------------------------



# ADMIN


@app.route('/manageprojects')
def admin():
    return render_template('admin/admin.html')

if __name__ == "__main__":
    app.run(debug=True)