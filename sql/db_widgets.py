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

    return db.select_all('widgets', {'user_ulid':user_ulid}, ['widget_name'],
                         ['widget_ulid', 'widget_name', 'description'])


def get_by_ulid(widget_ulid):
    """
    Get a widget by its ulid.
    """

    return db.select_single('widgets', {'widget_ulid':widget_ulid}, None,
                            ['widget_ulid', 'widget_name', 'user_ulid', 'user_email', 'description'])


def get_by_user_ulid_and_widget_name(user_ulid, widget_name):
    """
    Get a widget by its user ulid and widget name.
    """

    return db.select_single('widgets', {'user_ulid': user_ulid, 'widget_name': widget_name}, None,
                            ['widget_ulid', 'widget_name', 'user_ulid', 'user_email', 'description'])


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
