"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.

General purpose database utility functions.
"""

import lib.log as log
import sql.db as db

import ulid


con = db.get_connection()


def get_user_ulid_by_widget_ulid(widget_ulid):
    """
    Return the user_ulid of a widget, retrieved by its widget ulid.
    """

    try:

        widget = get_by_ulid(widget_ulid)

        if widget is None:
            return None

        return widget['user_ulid']

    except Exception as e:

        log.error('db_widgets.py::get_user_ulid_by_widget_ulid', str(e))
        return None


def get_by_user_ulid(user_ulid):
    """
    Get widgets by user ulid.
    """

    return db.select('widgets', {'user_ulid':user_ulid}, ['widget_name'],
                     ['widget_ulid', 'widget_name', 'description'])


def get_by_ulid(widget_ulid):
    """
    Get a widget by its ulid.
    """

    return db.select_single('widgets', {'widget_ulid':widget_ulid}, None,
                     ['widget_ulid', 'widget_name', 'user_ulid', 'user_email', 'description'])

    # try:
    #
    #     cur = con.cursor()
    #
    #     cur.execute(
    #         "SELECT widget_ulid, widget_name, user_ulid, user_email, description FROM widgets WHERE widget_ulid = %s",
    #         (widget_ulid,))
    #
    #     widget = cur.fetchone()
    #     con.commit()
    #
    #     if not widget:
    #         return None
    #
    #     widget_dict = db.create_dict(widget, ['widget_ulid', 'widget_name', 'user_ulid', 'user_email', 'description'])
    #
    #     return widget_dict
    #
    # except Exception as e:
    #
    #     log.error('db_widgets.py::get_by_user_ulid', str(e))
    #     con.commit()
    #     return None


def get_widget_by_user_ulid_and_widget_name(user_ulid, widget_name):
    """
    Get a widget by its user ulid and widget name.
    """

    try:

        cur = con.cursor()

        cur.execute(
            "SELECT widget_ulid, widget_name, user_ulid, user_email, description FROM widgets "
            + "WHERE user_ulid = %s AND widget_name = %s",
            (user_ulid, widget_name,))

        widget = cur.fetchone()
        con.commit()

        if not widget:
            return None

        widget_dict = db.create_dict(widget, ['widget_ulid', 'widget_name', 'user_ulid', 'user_email', 'description'])

        return widget_dict

    except Exception as e:

        log.error('db_widgets.py::get_widget_by_user_ulid_and_widget_name', str(e))
        con.commit()
        return None


def insert(widget_name, user_ulid, user_email, description):
    """
    Insert a new widget.
    """

    try:

        new_ulid = ulid.new().str
        cur = con.cursor()

        cur.execute("INSERT INTO widgets (widget_ulid, widget_name, user_ulid, user_email, description) "
                    + "VALUES (%s, %s, %s, %s, %s)", (new_ulid, widget_name, user_ulid, user_email, description))

        con.commit()
        return new_ulid

    except Exception as e:

        log.error('db_widgets.py::insert', str(e))
        con.commit()
        return None


def update(widget_ulid, widget_name, user_ulid, user_email, description):
    """
    Update an existing widget.
    """

    try:

        cur = con.cursor()

        cur.execute("UPDATE widgets SET widget_name = %s, user_ulid = %s, user_email = %s, description = %s "
                    + "WHERE widget_ulid = %s", (widget_name, user_ulid, user_email, description, widget_ulid))

        con.commit()
        return

    except Exception as e:

        log.error('db_widgets.py::update', str(e))
        con.commit()
        return


def delete_widget(widget_ulid):
    """
    Delete a widget.
    """

    try:

        cur = con.cursor()
        cur.execute("DELETE FROM widgets WHERE widget_ulid = %s", (widget_ulid,))
        con.commit()

        return

    except Exception as e:

        log.error('db_widgets.py::delete_widget', str(e))
        con.commit()
        return
