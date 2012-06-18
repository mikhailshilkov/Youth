from google.appengine.ext import db

class Param(db.Model):
    name = db.StringProperty()
    value = db.TextProperty()
    
def get(name):
    return Param.get_by_key_name(name).value
    
def add(name, value):
    new = Param(key_name=name)
    new.name = name
    new.value = value
    new.put()
