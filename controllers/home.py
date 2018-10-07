"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.
"""
from typing import Optional, Dict, Any

import lib.log as log
import sql.db_things as db_things
import sql.db_users as db_users
import sql.db_widgets as db_widgets

from flask import request, redirect, session, render_template, url_for, flash, Blueprint

home = Blueprint('home', __name__, template_folder="templates")


@home.route('/')
@home.route('/index')
def index():
    """
    Home page.
    """

    things = None
    user = None

    try:

        things: Optional[Dict[Any, Any]] = db_things.get('page.index.help')

        user_email = session.get('user_email')
        user = None

        if user_email is None:

            # non-user: show help
            things['pref_show_page_help'] = 'yes'

        else:

            user = db_users.get_by_email(user_email)

            if user is None:
                things['pref_show_page_help'] = 'yes'
            else:
                if user['pref_show_page_help'] == 'yes':
                    things['pref_show_page_help'] = 'yes'

        return render_template('index.html', things=things, user=user)

    except Exception as e:

        log.error('home.py::index', 'Error on home page, [' + str(e) + '].')
        flash('Oops! Something went sideways. We have been notified of the problem. Carry on.')
        return render_template('index.html', things=things, user=user)


@home.route('/sign_in', methods=['POST'])
def sign_in():
    """
    Sign a user in.
    """

    user_email = request.form['user_email']
    password = request.form['password']

    user = db_users.auth_by_email_and_password(user_email, password)

    if not user:
        log.alert('home.py::sign_in', 'Failed sign in attempt for email [' + user_email + '].')
        flash('Could not sign you in. Are you already a user? If not, please sign up.')
        return redirect(url_for('home.index'))

    session['authenticated'] = True
    session['user_email'] = user_email
    session['user_ulid'] = user['user_ulid']

    flash('Welcome back ' + user['full_name'] + '!')

    return redirect(url_for('home.dashboard'))


@home.route('/sign_up', methods=['POST'])
def sign_up():
    """
    Sign up a new user.
    """

    user_email = request.form['user_email']
    password = request.form['password']
    
    user = db_users.get_by_email(user_email)
    if user is not None:
        flash('A user with that email address already exists. Hmmm. Not you? Try another email address.')
        return redirect(url_for('home.index'))
    
    user = db_users.insert_user(user_email, password)

    if user is None:
        flash('Oops! Looks like something went sideways. We have been notified of the problem. Carry on.')
        return redirect(url_for('home.index'))

    session['authenticated'] = True
    session['user_email'] = user_email
    session['user_ulid'] = user['user_ulid']

    flash('Welcome to QuantumRocket!')

    return redirect(url_for('home.dashboard'))


@home.route('/sign_out', methods=['GET'])
def sign_out():
    """
    Sign a user out.
    """

    session.clear()

    return redirect(url_for('home.index'))


@home.route('/dashboard', methods=['GET'])
def dashboard():
    """
    The Dashboard displays all stats at a glance.
    """

    user_email = session.get('user_email')
    user = db_users.get_by_email(user_email)
    
    if user is None:
        log.error('home.py::dashboard', 'No user record for email [' + user_email + '].')
        flash('Oops! Looks like something went sideways. We have been notified of the problem. Carry on.')
        return redirect(url_for('home.index'))
        
    widgets = db_widgets.get_by_user_ulid(user['user_ulid'])
    things: Optional[Dict[Any, Any]] = db_things.get('page.dashboard.help')

    if user['pref_show_page_help'] == 'yes':
        things['pref_show_page_help'] = 'yes'

    return render_template('dashboard.html', widgets=widgets, things=things)
