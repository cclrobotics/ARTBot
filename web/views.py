#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

import datetime
import json
from __init__ import app, db, models, csrf
from flask import render_template, flash, redirect, url_for, request, Response
from sqlalchemy import desc, extract, sql
from flask_login import login_required

#Home page
@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
    return render_template('main.html')

@app.route('/receive_art', methods=['POST'])
def receive_art():
    data = request.json

    allowed_colors = [
      "pink",
      "orange",
      "teal",
      "yellow",
      "blue"
    ]

    title = data.pop('title')
    email = data.pop('email')
    for key in data:
        if key not in allowed_colors: data.pop(key)

    art_data = dict()
    art_data['title'] = title
    art_data['email'] = email
    art_data['submit_date'] = datetime.datetime.now()
    art_data['art'] = json.dumps(data)
    art_data['status'] = 'Submitted'

    db.session.add(models.artpieces(**art_data))
    db.session.commit()
    return 'Robot Art Loaded'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404