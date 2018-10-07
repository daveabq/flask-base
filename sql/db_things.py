"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.

Functions dealing with the 'things' table.
"""

import lib.log as log
import sql.db as db

con = db.get_connection()


def get(key):
    """
    Get a 'things' record by its key.
    """

    try:

        cur = con.cursor()
        cur.execute("SELECT key, value FROM things WHERE key = %s", (key,))
        thing = cur.fetchone()
        con.commit()

        if not thing:
            return None

        thing_dict = {key: thing[1]}
        return thing_dict

    except Exception as e:

        log.error('db_things::get', str(e))
        con.commit()
        return None


def get_like(key):
    """
    Get 'things' records by key (using 'LIKE').
    """

    try:

        cur = con.cursor()
        cur.execute("SELECT key, value FROM things WHERE key LIKE '%s' ORDER BY key", (key,))
        things = cur.fetchall()
        con.commit()

        if not things:
            return None

        thing_dict = {}

        for key, value in things.iteritems():
            thing_dict[key] = value

        return thing_dict

    except Exception as e:

        log.error('db_things::get_like', str(e))
        con.commit()
        return None
