"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.

General purpose database utility functions.
"""

import lib.log as log
import lib.kvpairs as kvpairs

import psycopg2 as sql


cfg = kvpairs.load(kvpairs.get_config_filename())
env = cfg['env']


"""
Query functions defined in files that live in sql/ need a database connection
to execute. The 'con' variable provides an app-wide connection to the database
using the credentials defined in the config file (/etc/quantumrocket.conf).
"""
con = sql.connect(
    host=cfg[env + '.db.host'],
    user=cfg[env + '.db.user'],
    password=cfg[env + '.db.password'],
    dbname=cfg[env + '.db.dbname']
)


def get_connection():
    """
    Get the long-running database connection.
    """

    return con


def create_dict(obj, columns):
    """
    Create a dict, given a database record and an ordered list of columns.
    Mind the order of column names in the columns list
    """

    try:

        new_obj = {}

        for col in range(len(columns)):
            new_obj[columns[col]] = obj[col]

        return new_obj

    except Exception as e:

        log.error('db.py::create_dict', str(e))
        return {}


def select_single(table, where, order_by, cols):
    """
    Call the select(...) function and return the first list element if the list is not empty, otherwise return None.
    """

    rows = select(table, where, order_by, cols)

    if rows:
        return rows[0]
    else:
        return None


def select(table, where, order_by, cols):
    """
    Execute a SELECT statement, based on the supplied parameters.

    Given the call:

        select('widgets', {'user_ulid':'01CS2P9P684BAA6NCHDDN4D704'}, ['widget_name'],
            ['widget_ulid', 'widget_name', 'description'])

        the following SQL will be created:

        SELECT widget_ulid, widget_name, description FROM widgets WHERE user_ulid = %s ORDER BY widget_name

    For this call, with more elements in both the 'where' and 'order_by' params:

        select('widgets', {'user_ulid':'01CS2P9P684BAA6NCHDDN4D704, 'user_email':'a@a.a'},
            ['widget_name', 'description'], ['widget_ulid', 'widget_name', 'description'])

        the following SQL will be created:

        SELECT widget_ulid, widget_name, description FROM widgets WHERE user_ulid = %s AND user_email = %s
        ORDER BY widget_name, description

    In both of the examples above, the where clause placeholders (%s) will be filled in with the appropriate
    right-side values of the 'where' parameter. So, the final SQL executed in the first example will be:

        SELECT widget_ulid, widget_name, description FROM widgets WHERE user_ulid = '01CS2P9P684BAA6NCHDDN4D704'
        ORDER BY widget_name

        and the final SQL executed in the second example will be:

        SELECT widget_ulid, widget_name, description FROM widgets WHERE user_ulid = '01CS2P9P684BAA6NCHDDN4D704'
        AND user_email = 'a@a.a' ORDER BY widget_name, description

    :param table: select from this table
    :param where: map of WHERE clause criteria
    :param order_by: list of ORDER BY criteria
    :param cols: select these columns
    :return:
    """

    try:

        cur: object = con.cursor()

        s = 'SELECT '

        for i, col in enumerate(cols):

            s += col

            if i < len(cols) - 1:
                s += ', '

        s += ' FROM ' + table
        s += ' WHERE '

        where_values = []

        for where_col, where_value in where.items():

            if where_values:
                s += " AND "

            s += where_col + ' = %s'

            where_values.append(where_value)

        if order_by:

            s += ' ORDER BY '

            for i, order_by_col in enumerate(order_by):

                s += order_by_col

                if i < len(order_by) - 1:
                    s += ', '

        cur.execute(s, (*where_values,))

        rows = cur.fetchall()
        con.commit()

        if not rows:
            return None

        row_list = []

        for row in rows:
            row_dict = create_dict(row, cols)
            row_list.append(row_dict)

        return row_list

    except Exception as e:

        log.error('db.py::select', str(e))
        con.commit()
        return None
