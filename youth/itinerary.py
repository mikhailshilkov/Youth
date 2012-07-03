#coding=utf-8

from lib import translit
from youth import utils
from youth import maps
from youth import bot

# Class that represents a Trip
class Trip(object):
    def __init__(self, title, from_location, to_location, expenses, duration, steps):
        self.title = title
        self.from_location = from_location
        self.to_location = to_location
        self.expenses = expenses
        self.duration = duration
        self.steps = steps
        self.change_action = None
        self.time_text = self.get_time_text()
        self.price_text = self.get_price_text()
    def get_price_text(self):
        return 'Expenses: ' + utils.price_to_string(self.expenses)
    def get_time_text(self):
        return 'Travel time: ' + utils.duration_to_string(self.duration)
    def jsonable(self):
        return self.__dict__
    
def get_directions(from_place, from_location, to_place, to_location, date, start_time):
    route = maps.get_transit_route(from_location, to_location)
    trip = create_trip(from_place, from_location, to_place, to_location, route, date, start_time)
    return trip                   

def create_trip(from_place, from_location, to_place, to_location, route, date, start_time):    
    steps_to = []
    duration = 0
    expenses = 0
    has_subway_info = False
    step_start_time = start_time
    
    # assign icons
    for i in range(len(route.directions)):
        step = route.directions[i]
        previous = route.directions[i-1] if i > 0 else None
        if step.is_subway():
            step.start_icon = step.end_icon = 'underground'
            step.start_name = step.end_name = 'Underground station'
            if previous != None and previous.is_walk():
                previous.end_icon = 'underground'
                previous.end_name = 'Underground station'
        elif step.is_land_transport():
            step.start_icon = step.end_icon = 'bus'
            step.start_name = step.end_name = 'Bus stop'
            if previous != None and previous.is_walk():
                previous.end_icon = 'bus'
                previous.end_name = 'Bus stop'
        elif step.is_walk():
            if previous != None:
                step.start_icon = previous.end_icon
                step.start_name = previous.end_name
    route.directions[0].start_icon = from_place.place_type
    route.directions[0].start_name = from_place.name
    route.directions[-1].end_icon = to_place.place_type
    route.directions[-1].end_name = to_place.name
    
    for step in route.directions: 
        if step.is_train():
            next_train = get_next_peterhot_train(date, step_start_time)
            step_start_time = next_train.departure
            hint = 'Train at ' + utils.time_to_string(next_train.departure)
            step.duration = next_train.get_duration()
        else:
            hint = step.addinfo
                        
        details = []
        if step.has_map:
            details.append({
                    'show_label': 'Show the map',
                    'hide_label': 'Hide the map',
                    'action': 'map',
                    'data' : step.get_route_json()
                    })
        if step.is_subway() and not has_subway_info:
            has_subway_info = True
            details.append({
                    'show_label': 'Learn about tokens',
                    'hide_label': 'Hide info',
                    'action': 'info',
                    'data' : '<i>To buy tokens you need to find ticket office which are normally located very close to the entrance [Bad English - correct] [TO DO: Check whether ticket machines have English interface] [TO DO: Add photo of ticket office]</i>'
                    })
        if step.hint != None:
            details.append({
                    'show_label': 'Show info',
                    'hide_label': 'Hide info',
                    'action': 'info',
                    'data' : '<i>' + step.hint + '</i>'
                    })
        steps_to.append({'instruction': translit.translify(step.direction),
                 'start_time': utils.time_to_string(step_start_time),
                 'hint' : hint,
                 'details' : details})
        step_start_time = utils.time_add_mins(step_start_time, step.duration)
        duration += step.duration
        expenses += step.transport.price if step.transport != None and step.transport.price != None else 0
    steps_to.append({'instruction': to_place.name,
                 'start_time': utils.time_to_string(step_start_time),
                 'hint' : ''})        
    total_duration = utils.time_get_delta_minutes(start_time, step_start_time)
    return Trip('Trip from ' + from_place.name + ' to ' + to_place.name, from_location.to_url_param(), to_location.to_url_param(), expenses, total_duration, steps_to)

def clean_post_subway_walk(route):
    if route.directions[-1].is_walk() and route.directions[-2].is_subway():
        route.directions.pop()
        
def get_next_peterhot_train(date, time_after):    
    timetable = bot.fetch_trains('Санкт-Петербург', 'Новый Петергоф', date)    
    return [x for x in timetable if x.departure > time_after][0]