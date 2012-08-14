import datetime
from youth import itinerary
from youth import place
from youth import utils
from google.appengine.ext import db
from collections import defaultdict

def get_all():
    all_ratings = [x for x in db.GqlQuery("SELECT * FROM RatingPart LIMIT 1000")]    
    res = defaultdict(list)
    for r in all_ratings: 
        res[r.hotel_name].append(r)
    result = []
    for hotel_name, ratings in res.items():
        duration =sum([x.duration for x in ratings])
        expenses =sum([x.expenses for x in ratings])
        metric =sum([x.metric for x in ratings])
        result.append(Rating(hotel_name, duration, expenses, metric))
    return sorted(result, key=lambda rating: rating.duration)

def get(hotel):    
    ratings = [x for x in db.GqlQuery("SELECT * FROM RatingPart WHERE hotel_name = '" + hotel.name + "' LIMIT 1000")]
    result = []    
    for place in ['State Hermitage', 'Peterhof: The Grand Palace', 'Peter and Paul Cathedral', "Saint Isaac's Cathedral", 'Pushkin: The Great Palace of Tsarskoye Selo', 'Pulkovo Airport', 'The State Russian Museum', 'Mariinsky Theatre']:
        result.append(get_rating(hotel, ratings, place))
    return result

def get_rating(hotel, ratings, place_name):
    sight_ratings = [x for x in ratings if x.place_name == place_name]
    if len(sight_ratings) > 0:
        sight_rating = sight_ratings[0]
    else:
        [to_place, to_location] = place.get_by_name(place_name)
        if to_place == None:
            raise Exception(place_name)
        date = datetime.date.today() + datetime.timedelta(days=1)
        time = datetime.time(hour=10, minute=0)
        trip = itinerary.get_directions(hotel, hotel.get_point(), to_place, to_location, date, time, 'o')
            
        sight_rating = RatingPart()
        sight_rating.hotel_name = hotel.name
        sight_rating.place_name = to_place.name
        sight_rating.place_name_rus = to_place.name_rus
        sight_rating.duration = trip.duration
        sight_rating.expenses = trip.expenses
        sight_rating.metric = trip.metric
        sight_rating.put()
    return sight_rating

class Rating(object):
    def __init__(self, hotel_name, duration, expenses, metric):
        self.hotel_name = hotel_name
        self.duration = duration
        self.expenses = expenses
        self.metric = metric
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