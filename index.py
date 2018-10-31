"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.
"""

import lib.kvpairs as kvpairs
import lib.log as log

from flask import Flask, request, redirect, session, url_for, flash

from controllers.home import home
from controllers.widget import widget
from controllers.profile import profile


cfg = kvpairs.load(kvpairs.get_config_filename())
log.debug('index.py', 'Initializing example Flask web app.')


app = Flask(__name__)

app.register_blueprint(home)
app.register_blueprint(widget)
app.register_blueprint(profile)

app.secret_key = '1324fluffy5678'
app.config['SESSION_TYPE'] = 'filesystem'


@app.before_request
def before_request():
    """
    Verify user has authenticated, except for non-secure pages.
    """

    if 'authenticated' not in session \
            and request.endpoint != 'home.index' \
            and request.endpoint != 'home.sign_in' \
            and request.endpoint != 'home.sign_up' \
            and request.endpoint != 'home.about' \
            and request.endpoint != 'home.terms':

        flash('Please sign in.')

        return redirect(url_for('home.index'))


if __name__ == '__main__':

    app.run(debug=True, use_reloader=True)
