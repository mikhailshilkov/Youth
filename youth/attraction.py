from google.appengine.ext import db
from google.appengine.api import memcache
from youth import utils

class Attraction(db.Model):
    name = db.StringProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    def get_latlng(self):
        return str(self.latitude) + ',' + str(self.longitude)
    def jsonable(self):
        return utils.model_to_dict(self)
    
def get(term):
    key = 'attractions'
    attractions = memcache.get(key) #@UndefinedVariable
    if attractions == None:
        attractions = [x for x in db.GqlQuery("SELECT * FROM Attraction LIMIT 1000")]
        memcache.add(key, attractions, 24*60*60) #@UndefinedVariable
        
    if term != None and term != '':
        result = [x for x in attractions if x.name.lower().startswith(term.lower())]
        if len(result) < 10:
            result.extend([x for x in attractions if x.name.lower().find(term.lower()) > 0])
        return result
    else:
        return attractions

def add(name, lat, lng):
    new_attraction = Attraction(key_name=name)
    new_attraction.name = name
    new_attraction.latitude = lat
    new_attraction.longitude = lng
    new_attraction.put()
    
def delete(name):
    key = db.Key.from_path('Attraction', name)
    db.delete(key)