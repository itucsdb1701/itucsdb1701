import datetime
import os
import json
import re
import psycopg2 as dbapi2
from flask import redirect, Blueprint, flash
from flask.helpers import url_for
from flask import Flask
from flask import render_template, Response
from flask import request, current_app
from classes import User
from passlib.apps import custom_app_context as pwd_context
from flask_login.utils import login_required
from flask_login import login_manager, login_user, logout_user, confirm_login,current_user
from urllib.parse import urlparse, urljoin
from user import link3


link1 = Blueprint('link1',__name__)
dsn = """user='vagrant' password='vagrant' host='localhost' port=5432 dbname='itucsdb'"""


@link1.route('/')
def home_page():
    if current_user.is_authenticated:
        if current_user.level == 1:
            return redirect(url_for('link4.admin_home'))
        else:
            return redirect(url_for('link3.userProfile'))
    now = datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime())

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@link1.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        Flag = current_app.store.verify_user(request.form['uname'], request.form['psw'])
        if Flag == 0:
            user = User(request.form['uname'],9999, "zzz", "zzz").get_user(User(request.form['uname'],9999, "zzz", "zzz").get_id())
            login_user(user)
            next = url_for('link3.userProfile')
            if not is_safe_url(next):
                return abort(400)
            confirm_login()
            if current_user.level == 1:
                return redirect(url_for('link4.admin_home'))
            else:
                return redirect(url_for('link3.userProfile'))
        elif Flag == -1:
            flash('Wrong password!')
        else:
            flash('No such user!')
        return redirect(url_for('link1.home_page'))
    else:
        flash('UNAUTHORIZED USER!!!')
        return redirect(url_for('link1.home_page'))

@link1.route('/signup', methods = ['GET', 'POST'])
def signup():
        return render_template('signup.html')

@link1.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('link1.home_page'))

@link1.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == "POST":
        userpsw0 = request.form['psw']
        userpwd1 = request.form['psw-repeat']
        if userpsw0 != userpwd1:
            flash('Passwords do not match!')
            return redirect(url_for('link1.signup'))
        else:
            userName = request.form['name']
            if checkusername(userName) == False:
                flash('Username is taken!')
                return redirect(url_for('link1.signup'))
            userNumber = request.form['studentno']
            useremail = request.form['email']
            userpsw = pwd_context.encrypt(userpsw0)
            nuser = User(userName,userNumber,useremail,userpsw)
            current_app.store.add_user(nuser)
        return render_template('home.html')

def checkusername(name):
    with dbapi2.connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """ SELECT COUNT(*) FROM CLUBDB WHERE (NAME = %s) """
        cursor.execute(query,(name,))
        if cursor.fetchone()[0] != 0:
            return True
        else:
            return False
