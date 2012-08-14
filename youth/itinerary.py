#coding=utf-8

from django.utils.translation import ugettext as _
from youth import utils
from youth import maps
from youth import bot
from youth import router

# Class that represents a Trip
class Trip(object):
    def __init__(self, title, from_location, to_location, expenses, duration, metric, steps):
        self.title = title
        self.from_location = from_location
        self.to_location = to_location
        self.expenses = expenses
        self.duration = duration
        self.metric = metric
        self.steps = steps
        self.change_action = None
        self.time_text = self.get_time_text()
        self.price_text = self.get_price_text()
    def get_price_text(self):
        return _('Expenses') + ': ' + utils.price_to_string(self.expenses)
    def get_time_text(self):
        return _('Travel time') + ': ' + utils.duration_to_string(self.duration)
    def jsonable(self):
        return self.__dict__
    
def get_directions(from_place, from_location, to_place, to_location, date, start_time, engine):
    route = maps.get_transit_route(from_location, to_location, engine)
    trip = create_trip(from_place, from_location, to_place, to_location, route, date, start_time)
    return trip                   

def create_trip(from_place, from_location, to_place, to_location, route, date, start_time):    
    steps_to = []
    duration = 0
    expenses = 0
    has_subway_info = False
    step_start_time = start_time
    
    # assign icons
    route.directions[0].start_icon = from_place.place_type
    route.directions[0].start_name = from_place.name_local
    for i in range(len(route.directions)):
        step = route.directions[i]
        previous = route.directions[i-1] if i > 0 else None
        if step.is_subway():
            step.start_icon = step.end_icon = 'underground'
            step.start_name = step.end_name = 'Underground station'
            if previous != None and previous.is_walk():
                previous.end_icon = 'underground'
                previous.end_name = 'Subway station'
        elif step.is_train():
            step.start_icon = step.end_icon = 'train'
            if previous != None and previous.is_walk():
                previous.end_icon = 'train'
            near_trains = get_nearest_trains(step, date, step_start_time)
            if near_trains != None:
                [prev_train, next_train] = near_trains 
                delta_prev = utils.time_get_delta_minutes(prev_train.departure, step_start_time)
                delta_next = utils.time_get_delta_minutes(step_start_time, next_train.departure)
                if delta_prev < delta_next * 2:
                    extra_wait_time = -delta_prev
                    train = prev_train
                else: 
                    extra_wait_time = delta_next
                    train = next_train
                start_time = utils.time_add_mins(start_time, extra_wait_time)
                steps_to.append({'instruction': 'You should leave at %s to fit train timetable' % utils.time_to_string(start_time),
                                 'start_time': ' ',
                                 'hint' : ''})
                step.duration = train.get_duration()
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
        step_start_time = utils.time_add_mins(step_start_time, step.duration)
    route.directions[-1].end_icon = to_place.place_type
    route.directions[-1].end_name = to_place.name_local
    
    step_start_time = start_time
    for i in range(len(route.directions)):
        step = route.directions[i]
        previous = route.directions[i-1] if i > 0 else None
        hint = step.get_default_addinfo()
        if step.is_train():
            steps_to[-1]['details'].append({
                'show_label': _('Learn about train tickets'),
                'hide_label': _('Hide info'),
                'action': 'info',
                'data' : "'" + _("Train tickets info HTML") + "'"
                })
                        
        details = []
        if step.has_map:
            details.append({
                    'show_label': _('Show the map'),
                    'hide_label': _('Hide the map'),
                    'action': 'map',
                    'data' : step.get_route_json()
                    })
        if step.is_subway() and not has_subway_info:
            has_subway_info = True
            details.append({
                    'show_label': _('Learn about tokens'),
                    'hide_label': _('Hide info'),
                    'action': 'info',
                    'data' : "'" + _("Tokens info HTML") + "'"
                    })
        if step.hint != None:
            details.append({
                    'show_label': 'Show info',
                    'hide_label': 'Hide info',
                    'action': 'info',
                    'data' : '<i>' + step.hint + '</i>'
                    })
        steps_to.append({'instruction': step.direction,
                 'start_time': utils.time_to_string(step_start_time),
                 'hint' : hint,
                 'details' : details})
        step_start_time = utils.time_add_mins(step_start_time, step.duration)
        duration += step.duration
        expenses += step.transport.price if step.transport != None and step.transport.price != None else 0
    steps_to.append({'instruction': to_place.name_local,
                 'start_time': utils.time_to_string(step_start_time),
                 'hint' : ''})        
    total_duration = utils.time_get_delta_minutes(start_time, step_start_time)
    return Trip(_('Trip from') + ' ' + from_place.name_local + ' ' + _('to') + ' ' + to_place.name_local, from_location.to_url_param(), to_location.to_url_param(), expenses, total_duration, route.get_cost(), steps_to)

def clean_post_subway_walk(route):
    if route.directions[-1].is_walk() and route.directions[-2].is_subway():
        route.directions.pop()
        
def get_nearest_trains(step, date, time_after):
    if step.transport != None and step.transport.start_code != None and step.transport.end_code != None:
        timetable = bot.fetch_trains(step.transport.start_code, step.transport.end_code, date)
        if timetable != None:    
            result = []
            result.append([x for x in timetable if x.departure < time_after][-1])
            result.append([x for x in timetable if x.departure >= time_after][0])
            return result