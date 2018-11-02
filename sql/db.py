"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.

General purpose database utility functions.
"""

import lib.log as log
import lib.kvpairs as kvpairs

import datetime
import psycopg2 as sql
import ulid


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


def get_date(dt):
    """
    Return a datetime as a formatted string.
    """

    t = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    return t.strftime('%Y-%m-%d %H:%M')


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


#
# The key_columns dict contains a map of database tables and their respective primary key column names.
# This is used by the insert() function to simplify the call.
#
key_columns = {
    'things': None,
    'users': 'user_id',
    'widgets': 'widget_id'
}


def insert(table, cols_and_values):
    """
    Execute an INSERT statement, based on the supplied parameters.

    Given the call:

        insert('widgets', {'widget_name': 'fluffy the pink bunny', 'description': 'super-mega-ultra bunny fluffiness'})

    the following SQL will be created:

        INSERT INTO widgets (widget_id, widget_name, description) VALUES (<new ulid>, 'fluffy the pink bunny',
            super-mega-ultra bunny fluffiness')

    The new ulid is returned.
    """

    try:

        cur: object = con.cursor()

        col_count = len(cols_and_values)
        element = 0
        s = 'INSERT INTO ' + table + ' ('

        key_col_name = key_columns[table]
        s += key_col_name + ', '

        col_values = []
        new_id = ulid.new().str
        col_values.append(new_id)

        for col_name in cols_and_values.keys():

            s += col_name

            if element < col_count - 1:
                s += ', '

            element += 1

            # skip the primary key column
            if col_name != key_col_name:
                col_values.append(cols_and_values[col_name])

        s += ') VALUES ('

        element = 0
        s += '%s, '  # primary key column

        for col_name in cols_and_values.keys():

            s += '%s'

            if element < col_count - 1:
                s += ', '

            element += 1

        s += ')'

        log.debug('db.py::insert', 'sql [' + s + ']')
        cur.execute(s, (*col_values,))
        con.commit()

        return new_id

    except Exception as e:

        log.error('db.py::insert', 'Error attempting to execute [' + s + ']. Error [' + str(e) + '].')
        con.commit()
        raise e


def update(table, where, cols_and_values):
    """
    Execute an UPDATE statement, based on the supplied parameters.

    Given the call:

        update('widgets', {'widget_id': '123'}, {'widget_name': 'fluffy the pink SUPER bunny',
            'description': 'super-mega-ultra bunny SUPER fluffiness'})

    the following SQL will be created:

        INSERT INTO widgets (widget_id, widget_name, description) VALUES (<new ulid>, 'fluffy the pink SUPER bunny',
            super-mega-ultra bunny SUPER fluffiness')

    The new ulid is returned.
    """

    try:

        cur: object = con.cursor()

        col_count = len(cols_and_values)
        element = 0
        s = 'UPDATE ' + table + ' SET '

        col_values = []

        for col_name, col_value in cols_and_values.items():

            s += col_name + ' = %s'

            if element < col_count - 1:
                s += ', '

            element += 1
            col_values.append(col_value)

        if where:

            s += ' WHERE '
            where_values = []

            for where_col, where_value in where.items():

                if where_values:
                    s += " AND "

                s += where_col + ' = %s'

                where_values.append(where_value)

        log.debug('db.py::update', 'sql [' + s + ']')

        values = col_values

        for where_value in where_values:
            values.append(where_value)

        if where:
            cur.execute(s, (*values,))
        else:
            cur.execute(s)

    except Exception as e:

        log.error('db.py::update', str(e))
        con.commit()
        return None


def select_single(table, where, order_by, cols):
    """
    Call the select(...) function and return the first list element if the list is not empty, otherwise return None.
    """

    rows = select(table, where, order_by, cols, False)

    if rows:
        return rows[0]
    else:
        return None


def select_single_like(table, where, order_by, cols):
    """
    Call the select(...) function and return the first list element if the list is not empty, otherwise return None.
    """

    rows = select(table, where, order_by, cols, True)

    if rows:
        return rows[0]
    else:
        return None


def select_all(table, where, order_by, cols):
    """
    Call the select(...) function and return all list elements if the list is not empty, otherwise return None.
    """

    rows = select(table, where, order_by, cols, False)

    if rows:
        return rows
    else:
        return None


def select_all_like(table, where, order_by, cols):
    """
    Call the select(...) function and return all list elements if the list is not empty, otherwise return None.
    """

    rows = select(table, where, order_by, cols, True)

    if rows:
        return rows
    else:
        return None


def select(table, where, order_by, cols, like):
    """
    Execute a SELECT statement, based on the supplied parameters.

    Given the call:

        select_all('widgets', {'user_id':'01CS2P9P684BAA6NCHDDN4D704'}, ['widget_name'],
            ['widget_id', 'widget_name', 'description'])

        the following SQL will be created:

        SELECT widget_id, widget_name, description FROM widgets WHERE user_id = %s ORDER BY widget_name

    For this call, we have more elements in both the 'where' and 'order_by' params:

        select('widgets', {'user_id':'01CS2P9P684BAA6NCHDDN4D704, 'user_email':'a@a.a'},
            ['widget_name', 'description'], ['widget_id', 'widget_name', 'description'])

        the following SQL will be created:

        SELECT widget_id, widget_name, description FROM widgets WHERE user_id = %s AND user_email = %s
        ORDER BY widget_name, description

    In both of the examples above, the where clause placeholders (%s) will be filled in with the appropriate
    right-side values of the 'where' parameter. So, the final SQL executed in the first example will be:

        SELECT widget_id, widget_name, description FROM widgets WHERE user_id = '01CS2P9P684BAA6NCHDDN4D704'
        ORDER BY widget_name

        and the final SQL executed in the second example will be:

        SELECT widget_id, widget_name, description FROM widgets WHERE user_id = '01CS2P9P684BAA6NCHDDN4D704'
        AND user_email = 'a@a.a' ORDER BY widget_name, description

    :param table: select from this table
    :param where: map of WHERE clause criteria
    :param order_by: list of ORDER BY criteria
    :param cols: select these columns
    :param like: use LIKE in the WHERE clause
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

        if where:

            s += ' WHERE '
            where_values = []

            for where_col, where_value in where.items():

                if where_values:
                    s += " AND "

                if like:
                    s += where_col + ' LIKE %s'
                else:
                    s += where_col + ' = %s'

                where_values.append(where_value)

        if order_by:

            s += ' ORDER BY '

            for i, order_by_col in enumerate(order_by):

                s += order_by_col

                if i < len(order_by) - 1:
                    s += ', '

        log.debug('db.py::select', 'sql [' + s + ']')

        if where:
            cur.execute(s, (*where_values,))
        else:
            cur.execute(s)

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
