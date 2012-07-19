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
    for i in range(len(route.directions)):
        step = route.directions[i]
        previous = route.directions[i-1] if i > 0 else None
        if step.is_subway():
            step.start_icon = step.end_icon = 'underground'
            step.start_name = step.end_name = 'Underground station'
            if previous != None and previous.is_walk():
                previous.end_icon = 'underground'
                previous.end_name = 'Subway station'
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
                    'data' : "'You need to buy tokens to enter to the metro:<br/>" + \
                             "<img src=\"/images/token1.jpg\" alt=\"Subway token\" height=\"120\" /><br/>" +\
                             "We would recommend you to buy them in token machine or at the ticket-office. Token machine works very simple way. You should place 100 rubles (one cash note) in the machine and it returns 3 tokens and a change (19 rubles). In the ticket office you can just provide required amount of money and show how many tokens you need. One token costs 27 rubles.<br/>" + \
                             "<img src=\"/images/token2.jpg\" alt=\"Token machine\" height=\"242\" /><img src=\"/images/token3.jpg\" alt=\"Ticket office\" height=\"242\" /><br/>" +\
                             "You can also buy a travel card if you need to use metro pretty frequently. You can buy 10 trips with 7 days limit on usage, 20 trips on 15 days, 40 or 50 trips on 30 days. It’s a bit cheaper than buy tokens. For example, 10 trips cost 230 rubles, 20 – 430 rubles, 40 and 50 const 830 and 1025 correspondingly. Additionally you should pay 30 ruble deposit to get plastic card. You can get money back if you return the card when you don’t need it. You do not need any document to get such card. To avoid verbal communication with operator you can just print and provide them the piece of paper with the following text:<br/>" + \
                             "<b>Пожалуйста, сделайте мне новую БСК на 10 поездок на 7 дней.</b><br/>" + \
                             "You can update numbers with one of combinations described below.<br/>" + \
                             "Be careful: you need to have a personal card for every traveler if you go together. You can not use the same travel card – after the usage travel card is blocked for 10 minutes.<br/>" + \
                             "<img src=\"/images/token4.jpg\" alt=\"Subway card\" height=\"120\" />'"
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