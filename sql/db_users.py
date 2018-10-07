"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.

Functions dealing with the 'users' table.
"""

import lib.log as log
import sql.db as db

import bcrypt
import psycopg2.extras
import psycopg2 as sql
import ulid


con = db.get_connection()


def auth_by_email_and_password(email, password):
    """
    Authenticate a user by their email and password.
    """

    try:

        cur = con.cursor()
        cur.execute("SELECT user_ulid, password, full_name FROM users WHERE email = %s", (email.lower(),))
        user = cur.fetchone()
        con.commit()

        if not user:
            return None

        user_dict = db.create_dict(user, ['user_ulid', 'password', 'full_name'])
        auth = bcrypt.checkpw(bytes(password, 'utf-8'), bytes(user_dict['password'], 'utf-8'))

        if auth:
            return user_dict
        else:
            return None

    except Exception as e:

        log.error('db_users.py::auth_by_email_and_password', str(e))
        con.commit()
        return None


def get_by_email(email):
    """
    Get a 'users' record by the user's email address.
    """

    try:

        cur = con.cursor()

        cur.execute("SELECT user_ulid, email, display_email, full_name, phone, status, pref_show_page_help "
                    + "FROM users WHERE email = %s", (email.lower(),))

        user = cur.fetchone()
        con.commit()

        if not user:
            return None

        user_dict = db.create_dict(user, ['user_ulid', 'email', 'display_email', 'full_name', 'phone', 'status',
                                          'pref_show_page_help'])

        return user_dict

    except Exception as e:

        log.error('db_users.py::get_by_email', str(e))
        con.commit()
        return None


def insert_user(email, password):
    """
    Insert a new 'users' record.
    :type email: str
    :type password: str
    """

    try:

        new_ulid = ulid.new().str
        hashed_password = bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt()).decode('utf-8')

        cur = con.cursor()
        sql.extras.register_uuid()

        cur.execute("INSERT INTO users (user_ulid, email, display_email, password) VALUES (%s, %s, %s, %s)",
                    (new_ulid, email.lower(), email, hashed_password))

        con.commit()

        user_dict = {'user_ulid': new_ulid, 'email': email}
        return user_dict

    except Exception as e:

        log.error('db_users.py::insert_user', str(e))
        con.commit()
        return None


def update(user_ulid, email, full_name, phone, pref_show_page_help):
    """
    Update an existing user.
    """

    try:

        cur = con.cursor()

        cur.execute("UPDATE users SET email = %s, full_name = %s, phone = %s, pref_show_page_help = %s "
                    + "WHERE user_ulid = %s", (email, full_name, phone, pref_show_page_help, user_ulid))

        con.commit()
        return

    except Exception as e:

        log.error('db_users.py::update', str(e))
        con.commit()
        return
