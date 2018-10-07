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
    host = cfg[env + '.db.host'],
    user = cfg[env + '.db.user'],
    password = cfg[env + '.db.password'],
    dbname = cfg[env + '.db.dbname']
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
