from google.appengine.ext import db
    
def get(name):
    parameter = Param.get_by_key_name(name)
    if parameter != None:
        return parameter.value
    
def add(name, value):
    new = Param(key_name=name)
    new.name = name
    new.value = value
    new.put()

class Param(db.Model):
    name = db.StringProperty()
    value = db.TextProperty()
