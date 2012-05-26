#coding=utf-8

from youth import utils
from youth import maps
from youth import bot

# Class that represents a Trip
class Trip(object):
    def __init__(self, title, expenses, duration, steps):
        self.title = title
        self.expenses = expenses
        self.duration = duration
        self.steps = steps
        self.change_action = None
        self.summary = self.get_summary()
    def get_summary(self):
        return 'Expenses: ' + str(self.expenses) + ' RUR, travel time: ' + utils.duration_to_string(self.duration)
    def jsonable(self):
        return self.__dict__

def get_trip(from_location, date, start_time, transport):
    if transport == 'meteor':
        route = maps.get_transit_route(from_location, '59.93993,30.309073')
        route.directions.append(maps.RouteStep('Take a speedboat. TODO: add more details.',
                                               60, 'About 1 hour', maps.Transport('Meteor', price = 500)))
        trip_to = create_trip('Way to Peterhof: Meteor (speed boat)', route, date, start_time)
    elif transport == 'train':
        route = maps.get_transit_route(from_location, '59.907486,30.299383')
        clean_post_subway_walk(route)
        route.directions.append(maps.RouteStep('Leave the subway on Baltiiskaya (Балтийская) and exit to the central railway station (Voksal - Вокзал). ' +
                                    'You may enter the railway station directly from subway entering hall following the directions. ' +
                                    'The orientation at the railway station is not difficult as soon as you are in the main hall. ' + 
                                    'All booking offices as well as platforms are located in one area. ',
                                    5, 'About 5 mins, 150 m', None))
        route.directions.append(maps.RouteStep('Buy tickets to the station Peterhof; the fare is 44 RUR for one person one way (88 for return ticket). ' +
                                               'We would recommend buying return ticket if you plan to use the same way to travel in both directions. ' +
                                               'The ticket is valid for the whole day so you don’t have to take any particular trains. ',
                                               5, 'About 5 mins', None))
        route.directions.append(maps.RouteStep('Take a train. You need to find a train in Ораниенбаум-1 direction.',
                                               0, '<Train at>', maps.Transport('Train', price = 44)))
        route.directions.append(maps.RouteStep('If the weather is fine take a stroll from railway station to the Peterhof palace (you can walk via park).',
                                               45, 'About 45 mins', None, maps.GeoPoint(59.864165, 29.925073), maps.GeoPoint(59.880511, 29.906809), True))
        
        trip_to = create_trip('Way to Peterhof: subway + suburban train', route, date, start_time)
    elif transport == 'bus':
        route = maps.get_transit_route(from_location, '59.86732529999999,30.261337499999968')
        clean_post_subway_walk(route)
        route.directions.append(maps.RouteStep('Cross the street through the underpass and find a bus stop',
                                    5, 'About 5 mins, 150 m', None, maps.GeoPoint(59.86758, 30.261308), maps.GeoPoint(59.868398, 30.259806), True))
        route.directions.append(maps.RouteStep('Take a minibus ("route-taxi"). Look for one of the following route numbers: К-424, ' +
                                    'K-424a, К-300, К-224, К-401a, К-404 or any route-taxi where you see word "Фонтаны" ' + 
                                    'on the window. Pay to driver, price may slightly vary. You should ask driver to stop in Peterhof.',
                                    60, 'About 1 hour', maps.Transport('Share taxi', 'К-424, K-424a, К-300, К-224, К-401a, К-404', None, 70)))
        route.directions.append(maps.RouteStep('Leave route taxi on Pravlentskaya ulitsa and go to Lower Park entry',
                                    10, 'About 10 mins, 800 m', None, maps.GeoPoint(59.883884, 29.911548), maps.GeoPoint(59.880511, 29.906809), True))
        trip_to = create_trip('Way to Peterhof: subway + bus', route, date, start_time)
    trip_to.change_action = 'Change transport'
            
    
    steps_in = [
        {'instruction': 'Buy the Lower Park tickets in a box office.' + 
                        'Our recommendation to visit Lower park and Upper park with all fountains at least. Also you can try to visit Grand palace you should be prepared to the huge queues. First one to buy tickets and another one to enter. Note that ticket in lower park works only for one visit. If you leave park you are not able to visit it again at the same day.',
         'start_time': utils.time_to_string(utils.time_add_mins(start_time, trip_to.duration)),
         'hint' : 'pay fare: XXX RUR'}]
    trip_in = Trip('Peterhof sightseeing', 0, 120, steps_in)    
            
    return [trip_to, trip_in]             

def get_options(from_location, date, start_time):
    trip_bus = get_trip(from_location, date, start_time, 'bus')[0]
    trip_meteor = get_trip(from_location, date, start_time, 'meteor')[0]
    trip_train = get_trip(from_location, date, start_time, 'train')[0]
    option_bus = {'alias': 'bus',
                  'title': 'Subway + bus',
                  'time': utils.duration_to_string(trip_bus.duration),
                  'experience': 'Poor',
                  'onfoot': '1,300 m',
                  'price': str(trip_bus.expenses) + ' RUR per person',
                  'simplicity': 'Average',
                  'icon': 'placeholder'}
    option_meteor = {'alias': 'meteor',
                  'title': 'Meteor (speed boat)',
                  'time': utils.duration_to_string(trip_meteor.duration),
                  'experience': 'Good',
                  'onfoot': '900 m',
                  'price': str(trip_meteor.expenses) + ' RUR per person',
                  'simplicity': 'Easy',
                  'icon': 'placeholder',
                  'risks': 'Risks: long queue before getting onboard'}
    option_train = {'alias': 'train',
                  'title': 'Subway + suburban train',
                  'time': utils.duration_to_string(trip_train.duration),
                  'experience': 'Poor',
                  'onfoot': '2,500 m',
                  'price': str(trip_train.expenses) + ' RUR per person',
                  'simplicity': 'Difficult',
                  'icon': 'placeholder'}
    return [option_bus, option_meteor, option_train]

def create_trip(title, route, date, start_time):    
    steps_to = []
    duration = 0
    expenses = 0
    step_start_time = start_time
    for step in route.directions: 
        if step.is_train():
            next_train = get_next_peterhot_train(date, step_start_time)
            step_start_time = next_train.departure
            hint = 'Train at ' + utils.time_to_string(next_train.departure)
            step.duration = next_train.get_duration()
        else:
            hint = step.addinfo
        steps_to.append({'instruction': step.direction,
                 'start_time': utils.time_to_string(step_start_time),
                 'hint' : hint,
                 'details' :
                 {
                    'show_label': 'Show the map',
                    'hide_label': 'Hide the map',
                    'action': 'map',
                    'map': { 'route' : step.get_route_json() }
                 } if step.has_map else None})
        step_start_time = utils.time_add_mins(step_start_time, step.duration)
        duration += step.duration
        expenses += step.transport.price if step.transport != None and step.transport.price != None else 0
    total_duration = utils.time_get_delta_minutes(start_time, step_start_time)
    return Trip(title, expenses, total_duration, steps_to)

def clean_post_subway_walk(route):
    if route.directions[-1].is_walk() and route.directions[-2].is_subway():
        route.directions.pop()
        
def get_next_peterhot_train(date, time_after):    
    timetable = bot.fetch_trains('Санкт-Петербург', 'Новый Петергоф', date)    
    return [x for x in timetable if x.departure > time_after][0]