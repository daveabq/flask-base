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

    return db.select_single('things', {'key': key}, None, ['key', 'value'])


def get_like(key):
    """
    Get 'things' records by key (using 'LIKE').
    """

    return db.select_all_like('things', {'key': key}, ['key', 'value'])
