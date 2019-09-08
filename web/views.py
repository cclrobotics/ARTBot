#views.py - Maps URLs to backend functions, then returns the results to the appropriate view

import datetime
import json
from __init__ import app, db, models, csrf
from flask import render_template, flash, redirect, url_for, request, Response
from sqlalchemy import desc, extract, sql
from flask_login import login_required

def parse_rgb(rgb_str):
    #converts an rgb string into a list and returns which color is biggest
    str_list = rgb_str[rgb_str.find('(') + 1: rgb_str.find(')')
                 ].split(',')
    int_list = [int(color.replace(" ","")) for color in str_list]
    max_position = int_list.index(max(int_list))
    max_color = ['red','green','blue'][max_position]
    return max_color


#Home page
@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
    return render_template('main.html')

@app.route('/receive_art', methods=['POST'])
def receive_art():
    art = request.json

    standardized_art = {'red':[]
                       ,'green':[]
                       ,'blue':[]}

    for color in art:
        if ((color != 'email') and (color != 'title')): 
            max_col = parse_rgb(color)
            standardized_art[max_col] += art[color]

    art_data = dict()
    art_data['title'] = art['title']
    art_data['email'] = art['email']
    art_data['submit_date'] = datetime.datetime.now()
    art_data['art'] = json.dumps(standardized_art)
    art_data['status'] = 'Submitted'

    db.session.add(models.artpieces(**art_data))
    db.session.commit()
    return 'Robot Art Loaded'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404