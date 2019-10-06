#!flask/bin/python
# run_webserver.py - Calls the __init__.py function (which runs all other required code), then starts the Flask server
from web import app

if __name__ == "__main__":
    app.run(debug=True)