"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.
"""

import lib.kvpairs as kvpairs
import lib.log as log
import sql.db_things as db_things
import sql.db_users as db_users

from flask import request, redirect, session, render_template, url_for, flash, Blueprint
from typing import Optional, Dict, Any, Union


profile = Blueprint('profile', __name__, template_folder="templates")
cfg = kvpairs.load(kvpairs.get_config_filename())


@profile.route('/my_profile', methods=['GET'])
def my_profile():
    """
    Display a user's profile.
    """

    try:

        user_email = session.get('user_email')
        user = db_users.get_by_email(user_email)

        things = db_things.get('page.my_profile.help')

        if user['pref_show_page_help'] == 'yes':
            things['pref_show_page_help'] = 'yes'

        return render_template('my_profile.html', user=user, things=things)

    except Exception as e:
        log.error('profile.py::my_profile', str(e))
        return redirect(url_for('home.dashboard'))


def get_user_from_request(req):
    """
    Create a user (in memory) from a request. This is used by update_profile
    if there is an error processing the user's input and we want to restore the
    user's input when rendering the my_profile.html page.
    """

    try:

        user: Dict[str, Union[str, Any]] = {}

        user['user_ulid'] = req.form['user_ulid']
        user['full_name'] = req.form['full_name']
        user['email'] = req.form['email']
        user['phone'] = req.form['phone']

        form = request.form
        pref_show_page_help = ''

        try:
            pref_show_page_help = form.getlist('pref_show_page_help')
        except Exception:
            log.debug('profile.py::get_user_from_request', 'pref_show_page_help NOT selected')

        if len(pref_show_page_help) > 0:
            user['pref_show_page_help'] = 'yes'
        else:
            user['pref_show_page_help'] = 'no'

        return user

    except Exception as e:

        log.error('profile.py::get_user_from_request', str(e))
        return None


@profile.route('/update_profile', methods=['POST'])
def update_profile():
    """
    Update a user's profile.
    """

    user_ulid = session.get('user_ulid')
    user_email = session.get('user_email')

    user = db_users.get_by_email(user_email)

    if user is None:
        log.error('profile.py::update_profile', 'ERROR: invalid state - no user record for user_email: ' + user_email)
        return redirect(url_for('home.index'))

    user_from_form: Optional[Dict[str, Union[str, Any]]] = get_user_from_request(request)

    # if the user is changing his/her email address,
    # check to make sure is doesn't already exist in the database

    if user_from_form['email'] != user_email:

        # check to see if the email address already exists
        check_email_user = db_users.get_by_email(user_from_form['email'])

        # if the email address is already taken, bail
        if check_email_user is not None:
            
            flash("The email address '" + user_from_form['email']
                  + "' is already in our system. Please try another email address.")

            return render_template('my_profile.html', user=user_from_form)

    email = user_from_form['email']
    full_name = user_from_form['full_name']
    phone = user_from_form['phone']
    pref_show_page_help = user_from_form['pref_show_page_help']

    db_users.update(user_ulid, email, full_name, phone, pref_show_page_help)

    flash('Your profile changes were successful.')
    return redirect(url_for('profile.my_profile'))
