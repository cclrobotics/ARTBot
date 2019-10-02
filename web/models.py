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

#Tracks some ongoing website variables
class site_vars(db.Model):
    var = db.Column(db.String(), primary_key=True)
    val = db.Column(db.Integer())

    def __repr__(self):
        return '<%r: %r>' % (self.var, self.val)


def model_exists(name):
    engine = db.get_engine()
    return engine.dialect.has_table(engine, name)

if not model_exists('site_vars'):
    print('No site_vars table found. Adding it.')
    db.create_all()
    db.session.add(site_vars(**{'var':'SUBMISSION_CNT','val':0}))
    db.session.commit()