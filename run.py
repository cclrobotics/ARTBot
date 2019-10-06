#!flask/bin/python
# run.py - Calls the __init__.py function (which runs all other required code), then starts the Flask server
from web import app
app.run(debug=True)