#models.py - Defines the database tables used in the website.

from __init__ import db


#Stores all submitted art and allows it to be referenced later by the robot interface
class artpieces(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    email = db.Column(db.String())
    submit_date = db.Column(db.DateTime())
    art = db.Column(db.String())
    status = db.Column(db.String())

    def __repr__(self):
        return '<%r: %r>' % (self.id, self.title)