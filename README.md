# flask-base
This is an example website using Flask. It demonstrates the use of Flask's Blueprint concept for help building modular applications. See: <a href="http://flask.pocoo.org/docs/0.12/blueprints/">Blueprints</a>. The app is known to run on Python 3.7.0.

Steps to get the example application up and running:

1. Clone or download this repository.
2. Create a Python virtual environment and activate it. I like to make my virtual environments independent of an application's code repo location (i.e. ~/bin/python/venv/flask)
3. Use pip to add the app's dependencies, found in ops/dependencies.sh.
4. Modify ops/quantumrocket.conf to suit your app and copy it to /etc.
5. Make sure you have an instance of PostgreSQL available.
6. Create the initial database (e.g. quantumrocket_dev) and role (e.g. qr). Grant the appropriate privileges (look at the commented lines at the top of ops/sql/initial database postgresql.sql) Be sure the database credentials in etc/quantumrocket.conf are valid for your database configuration.
7. Create the initial tables and indexes by using the SQL in ops/sql/initial database postgresql.sql.
8. At this point you should be able to run the app: $ python3 index.py

If there is any interest, I'd be happy to expand on this sparse document ;)
