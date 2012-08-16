from google.appengine.ext import db
from google.appengine.api import memcache
from youth import utils
from youth import maps
    
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
            if language == 'ru' and x.name_rus != None and x.name_rus != '':
                x.name_local = x.name_rus
            else:
                x.name_local = x.name
        places = attractions + hotels 
        memcache.add(key, places, 24*60*60) #@UndefinedVariable
        
    if term != None and term != '':
        result = [x for x in places if (x.name != None and x.name.lower().startswith(term.lower()))
                                    or (x.name_rus != None and x.name_rus.lower().startswith(term.lower()))]
        if len(result) < 10:
            result.extend([x for x in places if (x.name != None and x.name.lower().find(term.lower()) > 0) 
                                             or (x.name_rus != None and x.name_rus.lower().find(term.lower()) > 0)])
        return result
    else:
        return places
    
def cleanup():
    result = []
    hotels = [x for x in db.GqlQuery("SELECT * FROM Hotel LIMIT 1000")]
    for x in hotels:
        if x.fileName == None or x.fileName == '':
            result.append(x.name)
            delete_hotel(x.name)
    return result
    
def get_by_name(name, coord = ''):
    if name != '':
        places = get(name)
        if len(places) > 0:
            return [places[0], maps.GeoPoint(places[0].latitude, places[0].longitude)]        
    if coord != '':
        return [Address(name if name != '' else coord), maps.GeoPoint(*[float(x) for x in coord.split(',')])]
    
    return [None, None]    

def add_hotel(name, name_rus, file_name, rating, image_id, address, min_rate, lat, lng, hotel_type):
    new_hotel = Hotel(key_name=name)
    new_hotel.name = name
    new_hotel.name_rus = name_rus
    new_hotel.fileName = file_name
    new_hotel.rating = rating
    new_hotel.imageId = image_id
    new_hotel.address = address
    new_hotel.minRate = min_rate
    new_hotel.latitude = lat
    new_hotel.longitude = lng
    new_hotel.type = hotel_type     
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
    fileName = db.StringProperty()
    rating = db.FloatProperty()
    imageId = db.StringProperty()
    address = db.StringProperty()
    minRate = db.FloatProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    type = db.StringProperty() 
    def get_point(self):
        return maps.GeoPoint(self.latitude, self.longitude)
    def get_latlng(self):
        return str(self.latitude) + ',' + str(self.longitude)
    def get_min_rate(self):
        return utils.price_to_string(self.minRate) 
    def get_rating_range(self):
        return range(int(self.rating))
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
        self.name_local = name
        self.place_type = 'address'