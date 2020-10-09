# -*- encoding: utf-8 -*-

import requests
import os 
from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
import pandas as pd
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
            return redirect(url_for('base_blueprint.login   '))

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

@blueprint.route('/register/volunteers', methods=['GET', 'POST'])
def register_volunteers():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    
    return render_template( 'accounts/volunteers_register.html', form=create_account_form)

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

@blueprint.route('/students_add', methods=["POST"])
def add_student():
    if request.method == "POST":
        url = 'http://danieltan.org:8080/students/update'
        res = requests.post(url, data=request.form)
    render_template('students_view.html')

@blueprint.route('/programs_view')
def return_programs():
    response = requests.get("http://danieltan.org:8080/programs/all")
    data = response.json()
    for k in data:
        data = data[k]

    return render_template('programs_view.html', data=data)

@blueprint.route('/programs_add', methods=["GET", "POST"])
def add_program():

    if request.method == "POST":
        req = request.form
        url = 'http://danieltan.org:8080/programs/update'
        x = requests.post(url, data = req)
        return redirect(url_for('return_programs'))

    return render_template('programs_add.html')

@blueprint.route('/programs_edit')
def edit_program():
    return render_template('programs_edit.html')
