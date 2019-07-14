#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

import datetime
from __init__ import app, db, models, csrf
from flask import render_template, flash, redirect, url_for, request, Response
from sqlalchemy import desc, extract, sql
from flask_login import login_required

#Home page
@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
    return render_template('main.html')

@app.route('/receive_art', methods=['GET','POST'])
def receive_art():
    art = request.json

    art_data = dict()
    art_data['title'] = 'My Cool Test Art'
    art_data['email'] = 'raddude88@chillmail.com'
    art_data['submit_date'] = datetime.datetime.now()
    art_data['art'] = art
    art_data['status'] = 'Submitted'

    print(art_data)

    db.session.add(models.artpieces(**art_data))
    db.session.commit()
    return 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404