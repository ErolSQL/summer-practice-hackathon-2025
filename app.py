from flask import Flask, url_for, render_template, jsonify, session, request, redirect
import smtplib
from models import db, User, OTP, Project, Comment
import random
import os
import string
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta
from dotenv import load_dotenv



basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


app = Flask(__name__)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gitgud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
app.secret_key = os.getenv('SECRET_KEY')



def generate_otp():
    return ''.join(random.choices(string.digits, k=8))

db.init_app(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def send_email(to_email, code):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    from_email = EMAIL_USER
    password = EMAIL_PASSWORD

    subject = 'Your verification code'
    body = f'Your code is: {code}'

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, message)


@app.route('/request-otp', methods=['POST'])
def request_otp():
    email = request.form.get('email')
    code = generate_otp()

    OTP.query.filter_by(email=email).delete()

    otp_entry = OTP(email=email, code=code, created_at=datetime.utcnow())
    db.session.add(otp_entry)
    db.session.commit()

    send_email(email, code)

    
    return '', 204

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    code = request.form.get('code')
    confirm_code = request.form.get('confirm_code')

    if code != confirm_code:
        return "Codes do not match", 400

    otp_entry = OTP.query.filter_by(email=email, code=code).first()

    if not otp_entry:
        return "Invalid code", 400

    if datetime.utcnow() - otp_entry.created_at > timedelta(minutes=1):
        return "Code expired", 400

    user = User.query.filter_by(email=email).first()
    if user:
        return "User already exists", 400

    user = User(email=email)
    db.session.add(user)
    db.session.commit()

    
    db.session.delete(otp_entry)
    db.session.commit()

    return redirect(url_for('login'))





@app.route('/login/send-otp', methods=['POST'])
def send_login_otp():
    email = request.form.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return "Account doesn't exist", 400

    code = generate_otp()

    OTP.query.filter_by(email=email).delete()

    otp_entry = OTP(email=email, code=code, created_at=datetime.utcnow())
    db.session.add(otp_entry)
    db.session.commit()

    send_email(email, code)

    return '', 204

@app.route('/login', methods=['POST'])
def verify_login():
    email = request.form.get('email')
    code = request.form.get('code')

    otp_entry = OTP.query.filter_by(email=email, code=code).first()

    if not otp_entry:
        return "Invalid code", 400

    if datetime.utcnow() - otp_entry.created_at > timedelta(minutes=1):
        return "Code expired", 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return "Account doesn't exist", 400


    db.session.delete(otp_entry)
    db.session.commit()


    session['user_id'] = user.id

    return redirect(url_for('account'))






UPLOAD_FOLDER = 'storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  

@app.route('/submit-project', methods=['POST'])
def submit_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form.get('projectTitle')
    client_name = request.form.get('clientName')
    project_type = request.form.get('projectType')
    description = request.form.get('projectDescription')

    new_project = Project(
        user_id=session['user_id'],
        title=title,
        client_name=client_name,
        project_type=project_type,
        description=description
    )

    db.session.add(new_project)
    db.session.commit()

    project_folder = os.path.join(UPLOAD_FOLDER, str(new_project.id))
    os.makedirs(project_folder, exist_ok=True)

    files = request.files.getlist('projectFile')
    for file in files:
        if file and file.filename:

            relative_path = file.filename
            safe_path = os.path.normpath(relative_path)  # normalizeaza path-ul
            full_path = os.path.join(project_folder, safe_path)


            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            file.save(full_path)

    return redirect(url_for('account'))














# ---------------------------------------------- PAGINI ----------------------------------------------


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def registerpage():
    return render_template('register.html')

@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    projects = Project.query.filter_by(user_id=user.id).all()


    for project in projects:
        project_folder = os.path.join(UPLOAD_FOLDER, str(project.id))
        if os.path.exists(project_folder):
            project.files = os.listdir(project_folder)
        else:
            project.files = []

    return render_template('account.html', email=user.email, projects=projects)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))









# ---------------------------------------------- PAGINI ----------------------------------------------



# ADMIN


@app.route('/manageprojects')
def admin():
    return render_template('admin/admin.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
