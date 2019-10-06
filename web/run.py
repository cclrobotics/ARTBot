#!flask/bin/python
# run.py - Calls the __init__.py function (which runs all other required code), then starts the Flask server
from __init__ import app
app.run(host='0.0.0.0',debug=False)