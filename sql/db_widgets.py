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


def get_user_id_by_widget_id(widget_id):
    """
    Return the user_id of a widget, retrieved by its widget ulid.
    """

    try:

        widget = find_by_id(widget_id)

        if widget is None:
            return None

        return widget['user_id']

    except Exception as e:

        log.error('db_widgets.py::get_user_id_by_widget_id', str(e))
        return None


def find_by_user_id(user_id):
    """
    Get widgets by user ulid.
    """

    return db.select_all('widgets', {'user_id':user_id}, ['widget_name'],
                         ['widget_id', 'widget_name', 'description'])


def find_by_id(widget_id):
    """
    Get a widget by its ulid.
    """

    return db.select_single('widgets', {'widget_id':widget_id}, None,
                            ['widget_id', 'widget_name', 'user_id', 'user_email', 'description'])


def find_by_user_id_and_widget_name(user_id, widget_name):
    """
    Get a widget by its user ulid and widget name.
    """

    return db.select_single('widgets', {'user_id': user_id, 'widget_name': widget_name}, None,
                            ['widget_id', 'widget_name', 'user_id', 'user_email', 'description'])


def delete_widget(widget_id):
    """
    Delete a widget.
    """

    try:

        cur = con.cursor()
        cur.execute("DELETE FROM widgets WHERE widget_id = %s", (widget_id,))
        con.commit()

        return

    except Exception as e:

        log.error('db_widgets.py::delete_widget', str(e))
        con.commit()
        return
