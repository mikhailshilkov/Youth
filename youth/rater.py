import datetime
from youth import itinerary
from youth import place
from youth import utils
from google.appengine.ext import db
from google.appengine.api import memcache
from collections import defaultdict

def get_all():
    key = 'ratings_all'
    data = memcache.get(key) #@UndefinedVariable
    if data is not None:
        return data

    all_ratings = [x for x in db.GqlQuery("SELECT * FROM RatingPart")]
            
    rating_dict = defaultdict(list)
    for r in all_ratings: 
        if r.duration != None:
            rating_dict[r.hotel_name].append(r)
    hotel_dict = dict()
    for h in place.get_hotels():
        hotel_dict[h.name] = h
            
    result = []
    for hotel_name, ratings in rating_dict.items():
        if len(ratings) >= 8:
            duration =sum([x.duration for x in ratings])
            expenses =sum([x.expenses for x in ratings])
            metric =sum([x.metric for x in ratings])
            name_rus = hotel_dict[hotel_name].name_rus
            result.append(Rating(hotel_name, name_rus, duration, expenses, metric))
    result = sorted(result, key=lambda rating: rating.duration)
    memcache.add(key, result, 24*60*60) #@UndefinedVariable
    return result

def get(hotel):    
    ratings = [x for x in db.GqlQuery("SELECT * FROM RatingPart WHERE hotel_name = :1 LIMIT 1000", hotel.name)]
    result = []
    for place in ['Pulkovo Airport', 'State Hermitage', 'Peter and Paul Cathedral', "Saint Isaac's Cathedral", 'Peterhof: The Grand Palace', 'Pushkin: The Great Palace of Tsarskoye Selo', 'The State Russian Museum', 'Mariinsky Theatre']:
        result.append(get_rating(hotel, ratings, place))
    return result

def get_rating(hotel, ratings, place_name):
    sight_ratings = [x for x in ratings if x.place_name == place_name]
    sight_rating = None
    if len(sight_ratings) > 0:
        sight_rating = sight_ratings[0]
    else:
        [to_place, to_location] = place.get_by_name(place_name)
        if to_place == None:
            raise Exception(place_name)
        date = datetime.date.today() + datetime.timedelta(days=1)
        time = datetime.time(hour=10, minute=0)
        trip = itinerary.get_directions(hotel, hotel.get_point(), to_place, to_location, date, time, 'o')
            
        if trip.duration != None:
            sight_rating = RatingPart()
            sight_rating.hotel_name = hotel.name
            sight_rating.place_name = to_place.name
            sight_rating.place_name_rus = to_place.name_rus
            sight_rating.duration = trip.duration
            sight_rating.expenses = trip.expenses
            sight_rating.metric = trip.metric
            sight_rating.put()
    return sight_rating

def cleanup(hotel_name):
    ratings = [x for x in db.GqlQuery("SELECT * FROM RatingPart WHERE hotel_name = :1 LIMIT 1000", hotel_name)]
    for r in ratings:
        db.delete(r.key)

class Rating(object):
    def __init__(self, hotel_name, hotel_name_rus, duration, expenses, metric):
        self.hotel_name = hotel_name
        self.hotel_name_rus = hotel_name_rus
        self.duration = duration
        self.expenses = expenses
        self.metric = metric
    def hotel_name_local(self):
        return self.hotel_name_rus if utils.get_language() == 'ru' and self.hotel_name != '' else self.hotel_name
    def duration_string(self):
        return utils.duration_to_string(self.duration)
    def expenses_string(self):
        return utils.price_to_string(self.expenses)

class RatingPart(db.Model):
    hotel_name = db.StringProperty()
    place_name = db.StringProperty()
    place_name_rus = db.StringProperty()
    duration = db.IntegerProperty()
    expenses = db.IntegerProperty()
    metric = db.FloatProperty()
    def place_name_local(self):
        return self.place_name_rus if utils.get_language() == 'ru' else self.place_name
    def duration_text(self):
        return utils.duration_to_string(self.duration)
    def expenses_text(self):
        return utils.price_to_string(self.expenses)