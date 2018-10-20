"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.
"""

import lib.log as log
import sql.db as db
import sql.db_users as db_users
import sql.db_widgets as db_widgets
import sql.db_things as db_things

from flask import request, redirect, session, render_template, url_for, flash, Blueprint
from typing import Optional, Dict, Any


widget = Blueprint('widget', __name__, template_folder="templates")


@widget.route('/my_widgets', methods=['GET'])
def my_widgets():
    """
    Display a user's widgets.
    """

    widgets = []
    user = None

    try:

        user_email = session.get('user_email')

        user = db_users.get_by_email(user_email)

        if user is None:
            log.error('widget.py::my_widgets', 'ERROR: invalid state - no user record for user_email: ' + user_email)
            flash('Please sign in. If you are not already a QuantumRocket user, please sign up.')
            return redirect(url_for('home.index'))

        widgets = db_widgets.get_by_user_ulid(user['user_ulid'])

    except Exception as e:

        log.error('widget.py::my_widgets', str(e))

    things = db_things.get('page.my_widgets.help')

    if user['pref_show_page_help'] == 'yes':
        things['pref_show_page_help'] = 'yes'

    return render_template('my_widgets.html', widgets=widgets, things=things)


def get_widget_from_request(req):
    """
    Create a widget (in memory) from a request. This is used if there is an error
    processing the user's input and we want to restore the user's input when
    rendering the add_widget.html page.
    """

    try:

        widget_from_request: Dict[str, Optional[Any]] = {}

        try:
            widget_from_request['widget_ulid'] = req.form['widget_ulid']
        except Exception:
            # if we are adding a new widget, there will not be a widget_ulid
            widget_from_request['widget_ulid'] = None

        widget_from_request['widget_name'] = req.form['widget_name']
        widget_from_request['description'] = req.form['description']

        return widget_from_request

    except Exception as e:

        log.error('widget.py::get_widget_from_request', str(e))
        return None


@widget.route('/add_widget', methods=['GET'])
def add_widget():
    """
    Start the process of adding a new widget.
    """

    return render_template('add_widget.html', widget=None)


@widget.route('/add_widget_complete', methods=['POST'])
def add_widget_complete():
    """
    Complete the process of adding a new widget.
    """

    user_ulid = session.get('user_ulid')
    user_email = session.get('user_email')

    user = db_users.get_by_email(user_email)

    if user is None:

        log.error('widget.py::add_widget_complete',
                  'ERROR: invalid state - no user record for user_email: ' + user_email)

        flash('Please sign in. If you are not already a QuantumRocket user, please sign up.')
        return redirect(url_for('home.index'))

    widget_name = request.form['widget_name']

    # check to see if the widget name already exists
    existing_widget: Optional[Dict[Any, Any]] = \
        db_widgets.get_by_user_ulid_and_widget_name(user_ulid, widget_name)

    if existing_widget is not None:

        flash("You already have a Widget with the name '" + widget_name
              + "'. Please try a different name as Widget names are unique.")

        keep_widget: Optional[Dict[str, Optional[Any]]] = get_widget_from_request(request)
        return render_template('add_widget.html', widget=keep_widget)

    description = request.form['description']

    widget = {}
    widget['widget_name'] = request.form['widget_name']
    widget['user_ulid'] = user_ulid
    widget['user_email'] = user_email
    widget['description'] = description

    widget_ulid = db.insert('widgets', widget)

    flash("Widget '" + widget_name + "' added.")
    log.debug('widget.py::add_widget_complete', 'Added new widget, widget_ulid [' + widget_ulid + '].')
    
    return redirect(url_for('widget.my_widgets'))


@widget.route('/delete_widget', methods=['POST'])
def delete_widget():
    """
    Delete a widget.

    This endpoint is called by the 'delete' action button,
    from the 'widgets' table on the my_widgets.html page.
    """

    widget_ulid = request.form['widget_ulid']
    log.debug('widget.py::delete_widget', 'widget_ulid [' + widget_ulid + ']')

    widget_to_delete: Optional[Dict[Any, Any]] = db_widgets.get_by_ulid(widget_ulid)
    widget_name = widget_to_delete['widget_name']

    # now we can safely delete the widget
    db_widgets.delete_widget(widget_ulid)

    flash("Widget name '" + widget_name + "' has been deleted.")
    log.debug('widget.py::delete_widget', 'deleted widget, widget_ulid [' + widget_ulid + ']')

    return redirect(url_for('widget.my_widgets'))


@widget.route('/edit_widget', methods=['GET'])
def edit_widget():
    """
    Edit a widget.

    This endpoint is called by an 'edit' action button,
    from the 'widgets' table on the my_widgets.html page.
    """

    user_ulid = session.get('user_ulid')
    user_email = session.get('user_email')

    user = db_users.get_by_email(user_email)

    if user is None:
        log.error('widget.py::edit_widget', 'ERROR: invalid state - no user record for user_email: ' + user_email)
        flash('Please sign in. If you are not already a user, please sign up.')
        return redirect(url_for('home.index'))

    widget_ulid = request.args.get('widget_ulid')

    if widget_ulid is None:

        log.error('widget.py::edit_widget',
                  'ERROR: invalid state - no widget_ulid in request. user_ulid [' + user_ulid + ']')

        flash('Oops! Something went sideways. We have been notified of the problem. Carry on.')
        return redirect(url_for('widget.my_widgets'))

    log.debug('widget.py::edit_widget', 'widget_ulid [' + widget_ulid + ']')

    widget_to_edit: Optional[Dict[Any, Any]] = db_widgets.get_by_ulid(widget_ulid)

    if widget_to_edit is None:

        log.error('widget.py::edit_widget',
                  'ERROR: invalid state - no widget record for widget_ulid [' + widget_ulid + ']')

        flash('Oops! Something went sideways. We have been notified of the problem. Carry on.')
        return redirect(url_for('widget.my_widgets'))

    return render_template('edit_widget.html', widget=widget_to_edit)


@widget.route('/edit_widget_complete', methods=['POST'])
def edit_widget_complete():
    """
    Complete a widget edit.
    """

    widget_ulid = request.form['widget_ulid']
    widget_name = request.form['widget_name']
    description = request.form['description']

    user_ulid = session.get('user_ulid')
    user_email = session.get('user_email')

    user = db_users.get_by_email(user_email)

    if user is None:

        log.error('widget.py::edit_widget_complete',
                  'ERROR: invalid state - no user record for user_email: ' + user_email)

        flash('Please sign in. If you are not already a user, please sign up.')
        return redirect(url_for('home.index'))

    # check to see if the widget name already exists
    existing_widget = db_widgets.get_by_user_ulid_and_widget_name(user_ulid, widget_name)

    if existing_widget is not None:

        # are we looking at the same widget (database and form)?
        if existing_widget['widget_ulid'] != widget_ulid:

            flash("You already have a Widget with the name '" + widget_name
                  + "'. Please try a different name as Widget names are unique.")

            keep_widget = get_widget_from_request(request)
            return render_template('edit_widget.html', widget=keep_widget)

    widget = {}
    widget['widget_name'] = widget_name
    widget['user_ulid'] = user_ulid
    widget['user_email'] = user_email
    widget['description'] = description

    db.update('widgets', {'widget_ulid': widget_ulid}, widget)

    flash("Widget '" + widget_name + "' edit successful.")

    log.debug('widget.py::edit_widget_complete',
              'Successful edit of existing widget, widget_ulid [' + widget_ulid + '].')

    return redirect(url_for('widget.my_widgets'))


def replace_widget(widgets, new_widget):
    """
    Replace a widget in a widget list.
    """

    for pos, current_widget in enumerate(widgets):

        if current_widget['widget_ulid'] == new_widget['widget_ulid']:
            widgets[pos] = new_widget
