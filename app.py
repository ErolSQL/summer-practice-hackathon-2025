from flask import Flask, url_for, render_template, jsonify, session, request, redirect
import smtplib
from models import db, User, OTP, Project, Comment
import random
import os
import string
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
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
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'storage')
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



def generate_otp():
    return ''.join(random.choices(string.digits, k=8))

db.init_app(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            return "User already exists", 400
        hashed_pw = generate_password_hash(password)
        user = User(email=email, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return "Invalid credentials", 400
        session['user_id'] = user.id
        return redirect(url_for('account'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
























# ---------------------------------------------- PAGINI ----------------------------------------------


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/login')
def loginpage():
    return render_template("login.html")

@app.route('/register')
def registerpage():
    return render_template('register.html')


@app.route('/projects')
def projects():
    return render_template('projects.html')






@app.route('/account')
def account():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # sau registerpage, după caz

    user = User.query.get(user_id)
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('login'))

    return render_template('account.html', user=user)





@app.route('/logout')
def logoutpage():
    session.pop('user_id', None)
    return redirect(url_for('home'))




@app.route('/projects-page')
def projects_page():
    return render_template('projects-page.html')




# ---------------------------------------------- PAGINI ----------------------------------------------



# ADMIN


@app.route('/manageprojects')
def admin():
    return render_template('admin/admin.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
