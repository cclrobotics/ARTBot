#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

import datetime
import json
from utilities import check_failed_validation, rebuild_art
from __init__ import app, db, models, csrf
from flask import render_template, flash, redirect, url_for, request, Response
from sqlalchemy import desc, extract, sql
from flask_login import login_required
from utilities import rebuild_art

#Home page
@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
    return render_template('main.html')

@app.route('/receive_art', methods=['POST'])
def receive_art():
    data = request.json

 ##added art to test db
    
    title = data.pop('title')
    email = data.pop('email')
    art = data.pop('art')
    picture = rebuild_art(art)

    # perform string validations
    failed_validation = check_failed_validation(title, email, art)
    
    if failed_validation:
        return failed_validation
    
    # passed validation so commit to DB
    art_data = dict()
    art_data['title'] = title
    art_data['email'] = email
    art_data['submit_date'] = datetime.datetime.now()
    art_data['art'] = json.dumps(art)
    art_data['status'] = 'Submitted'
    art_data['picture'] = picture

    db.session.add(models.artpieces(**art_data))
    db.session.commit()
    return 'Robot Art Loaded'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404