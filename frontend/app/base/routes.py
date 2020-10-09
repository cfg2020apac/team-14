# -*- encoding: utf-8 -*-
from dotenv import load_dotenv
load_dotenv()
import requests
import os
from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User
import json

from app.base.util import verify_pass

@blueprint.route('/')
def route_default():
    return render_template('main.html')

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.login'))

        # Something (user or pass) is not ok
        return render_template( 'accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'accounts/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Email already registered', 
                                    success=False,
                                    form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template( 'accounts/register.html', 
                                msg='User created please <a href="/login">login</a>', 
                                success=True,
                                form=create_account_form)

    else:
        return render_template( 'accounts/register.html', form=create_account_form)

# GET
@blueprint.route('/register/volunteers', methods=['GET'])
def register_volunteers():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    
    return render_template('accounts/volunteers_register.html', form=create_account_form)

# POST
@blueprint.route('/register/volunteers', methods=['POST'])
def register_volunteers_post():
    url = 'http://danieltan.org:8080/volunteers/update'
    res = requests.post(url, data=request.form)

    print(res)
    # 200 means http ok
    if res.status_code == 200:
        return render_template('accounts/volunteers_register_success.html') # change to success
    else:
        return render_template('accounts/volunteers_register.html', error=True)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500

### STRIKES TO RETURN DATA ###
@blueprint.route('/students_view')
def return_students():
    response = requests.get("http://danieltan.org:8080/students/all")
    
    data = response.json()
    for k in data:
        data = data[k]

    return render_template('students_view.html', data=data)

@blueprint.route('/students_add', methods=["GET", "POST"])
def add_student():

    if request.method == "POST":
        print(request.form)
        url = 'http://danieltan.org:8080/students/update'
        # url = 'http://requestbin.net/r/1l6imqw1'
        res = requests.post(url, data = request.form)
        # 200 means http ok
        return redirect(url_for('base_blueprint.return_students'))
            

    return render_template('students_add.html')

@blueprint.route('/students_edit/<email>')
def find_student(email):
    response = requests.get("http://danieltan.org:8080/students/find?email=" + email)
    data = response.json()

    return render_template('students_edit.html', data=data)

@blueprint.route('/programs_view')
def return_programs():
    response = requests.get("http://danieltan.org:8080/programs/all")
    data = response.json()
    for k in data:
        data = data[k]
    print(data)

    return render_template('programs_view.html', data=data)

@blueprint.route('/programs_add', methods=["GET", "POST"])
def add_program():

    if request.method == "POST":
        url = 'http://danieltan.org:8080/programs/update'
        # url = 'http://requestbin.net/r/1l6imqw1'
        res = requests.post(url, data = request.form)
        # 200 means http ok
        return redirect(url_for('base_blueprint.return_programs'))
            

    return render_template('programs_add.html')

@blueprint.route('/programs_edit/<program_id>')
def find_program(program_id):
    response = requests.get("http://danieltan.org:8080/programs/find?program_id=" + program_id)
    data = response.json()
    print(data)
    return render_template('programs_edit.html', data=data)
    
@blueprint.route('/volunteers_view', methods=['GET'])
def volunteers_view():
    # column_names = ["age", "contact", "email", "first_name", "gender", "language", "last_name", "school"]
    # df = pd.DataFrame(columns = column_names)
    
    response = requests.get("http://danieltan.org:8080/volunteers/all")

    data = response.json()
    for k in data:
        data = data[k]

    return render_template('volunteers_view.html', data=data)

# POST
@blueprint.route('/volunteers_add', methods=['POST'])
def volunteers_add():
    url = 'http://danieltan.org:8080/volunteers/update'
    res = requests.post(url, data=request.form)

    print(res)
    # 200 means http ok
    if res.status_code == 200:
        return render_template('volunteers_add.html', success=True)
    else:
        return render_template('volunteers_add.html', error=True)

@blueprint.route('/volunteers_edit/<string:email>', methods=['GET'])
def volunteers_edit(email):
    url = 'http://danieltan.org:8080/volunteers/find?email=' + email
    res = requests.get(url)

    # 200 means http ok
    if res.status_code == 200:
        print(res, res.json())
        return render_template('volunteers_edit.html', data=res.json())
    else:
        return render_template('volunteers_edit.html', error=True)

@blueprint.route('/volunteers_edit/<string:email>', methods=['POST'])
def volunteers_edit_post(email):
    url = 'http://danieltan.org:8080/volunteers/update'
    res = requests.post(url, data=request.form)

    print(res)
    # 200 means http ok
    if res.status_code == 200:
        return render_template('volunteers_add.html')
    else:
        return render_template('volunteers_add.html')

@blueprint.route('/index')
def return_dashboard_count():
    response = requests.get("http://danieltan.org:8080/students/all")

    data_list = []

    data = response.json()
    for k in data:
        data = data[k]

    data_list.append(len(data))

    response = requests.get("http://danieltan.org:8080/programs/all")

    data = response.json()
    for k in data:
        data = data[k]

    data_list.append(len(data))

    response = requests.get("http://danieltan.org:8080/volunteers/all")

    data = response.json()
    for k in data:
        data = data[k]

    data_list.append(len(data))

    print(data_list)

    return render_template('index.html', data=data_list) 
