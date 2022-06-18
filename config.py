import os
SECRET_KEY = os.urandom(32)
# Grabbing the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enabling debug mode.
DEBUG = True

# Connecting to the database
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345@localhost:5432/fyyurapp'
