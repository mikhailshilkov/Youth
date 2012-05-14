from google.appengine.ext import db
from youth import utils

class Hotel(db.Model):
    name = db.StringProperty()
    address = db.StringProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    def jsonable(self):
        return utils.model_to_dict(self)
    
def get(term):
    hotels = [x for x in db.GqlQuery("SELECT * FROM Hotel LIMIT 1000")]
    if term != None and term != '':
        result = [x for x in hotels if x.name.lower().startswith(term.lower())]
        if len(result) < 10:
            result.extend([x for x in hotels if x.name.lower().find(term.lower()) > 0])
        return result
    else:
        return hotels

def add(name, address, lat, lng):
    new_hotel = Hotel(key_name=name)
    new_hotel.name = name
    new_hotel.address = address
    new_hotel.latitude = lat
    new_hotel.longitude = lng
    new_hotel.put()
    
def delete(name):
    key = db.Key.from_path('Hotel', name)
    db.delete(key)