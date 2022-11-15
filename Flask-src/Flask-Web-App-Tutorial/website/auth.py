from lxml import etree as ET
from flask import Blueprint, render_template, request, flash, redirect, url_for, Flask
from .models import User
#from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename


auth = Blueprint('auth', __name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/files'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                flash('Successful login!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        if request.form['action'] == 'Submit':
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm')

            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists.', category='error')
            elif len(email) < 4:
                flash('Email must be greater than 3 characters.', category='error')
            elif len(username) < 2:
                flash('Username must be greater than 1 character.', category='error')
            elif password != password_confirm:
                flash('Passwords don\'t match.', category='error')
            elif len(password) < 7:
                flash('Password must be at least 7 characters.', category='error')
            else:
                new_user = User(email=email, username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                return redirect(url_for('views.home'))


        elif request.form['action'] == 'Upload':
            file = request.files['file']
            file_location = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
            file.save(file_location)

            tree = ET.parse(file_location)
            root = tree.getroot()
            xemail, xusername, xpassword = root[0].text, root[1].text, root[2].text
            email, username, password = str(xemail),str(xusername), str(xpassword)
            data = [email, username, password]

            flash('File uploaded!', category='success')
            return render_template("sign_up.html", user=current_user, data=data)


    return render_template("sign_up.html", user=current_user)
