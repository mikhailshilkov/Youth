from google.appengine.ext import db
from google.appengine.api import memcache
from youth import utils
    
def get(term):
    language = utils.get_language()
    key = 'places_' + language
    places = memcache.get(key) #@UndefinedVariable
    if places == None:
        attractions = [x for x in db.GqlQuery("SELECT * FROM Attraction LIMIT 1000")]
        for x in attractions:
            x.place_type = 'airport' if x.name.find('Airport') > 0 else 'sight'
            if language == 'ru' and x.name_rus != None:
                x.name_local = x.name_rus
            else:
                x.name_local = x.name
        hotels = [x for x in db.GqlQuery("SELECT * FROM Hotel LIMIT 1000")]
        for x in hotels:
            x.place_type = 'hotel'
            if language == 'ru' and x.name_rus != None:
                x.name_local = x.name_rus
            else:
                x.name_local = x.name
        places = attractions + hotels 
        memcache.add(key, places, 24*60*60) #@UndefinedVariable
        
    if term != None and term != '':
        result = [x for x in places if x.name_local.lower().startswith(term.lower())]
        if len(result) < 10:
            result.extend([x for x in places if x.name_local.lower().find(term.lower()) > 0])
        return result
    else:
        return places

def add_hotel(name, name_rus, address, lat, lng):
    new_hotel = Hotel(key_name=name)
    new_hotel.name = name
    new_hotel.name_rus = name_rus
    new_hotel.address = address
    new_hotel.latitude = lat
    new_hotel.longitude = lng
    new_hotel.put()
    
def delete_hotel(name):
    key = db.Key.from_path('Hotel', name)
    db.delete(key)
            
def add_attraction(name, name_rus, lat, lng):
    new_attraction = Attraction(key_name=name)
    new_attraction.name = name
    new_attraction.name_rus = name_rus
    new_attraction.latitude = lat
    new_attraction.longitude = lng
    new_attraction.put()
    
def delete_attraction(name):
    key = db.Key.from_path('Attraction', name)
    db.delete(key)
    
class Hotel(db.Model):
    name = db.StringProperty()
    name_rus = db.StringProperty()
    address = db.StringProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    def get_latlng(self):
        return str(self.latitude) + ',' + str(self.longitude) 
    def jsonable(self):
        prop_dict = utils.model_to_dict(self)
        prop_dict['name_local'] = self.name_local
        return prop_dict
    
class Attraction(db.Model):
    name = db.StringProperty()
    name_rus = db.StringProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    
    name_local = None
    def get_latlng(self):
        return str(self.latitude) + ',' + str(self.longitude)
    def jsonable(self):
        prop_dict = utils.model_to_dict(self)
        prop_dict['name_local'] = self.name_local
        return prop_dict
    
class Address(object):
    def __init__(self, name):
        self.name = name
        self.place_type = 'address'