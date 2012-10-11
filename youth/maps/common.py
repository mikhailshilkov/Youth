#coding=utf-8

from django.utils.translation import ugettext as _
from youth import utils

# Class that represents a Route
class Route(object):
    def __init__(self, directions, engine = None):
        self.directions = directions
        self.engine = engine
        
    def get_duration(self):
        return sum([step.duration for step in self.directions])
    
    def get_walk_duration(self):
        return sum([step.duration for step in self.directions if step.is_walk()])
    
    def get_cost(self):
        return sum([step.get_cost() for step in self.directions])
    
    def has_transport(self, transport_type):
        return len([x for x in self.directions if x.transport != None and x.transport.type == transport_type]) > 0

# Class that represents a Route Step
class RouteStep(object):
    def __init__(self, direction = None, duration = None, addinfo = None, 
                 transport = None, start_location = None, end_location = None, 
                 has_map = False, hint = None):
        self.direction = direction
        self.duration = duration
        self.distance = None
        self.addinfo = addinfo
        self.start_location = start_location 
        self.end_location = end_location
        self.transport = transport
        self.has_map = has_map
        self.hint = hint
        self.start_icon = None
        self.end_icon = None
        self.start_name = ''
        self.end_name = ''
        
    def is_subway(self):
        return self.transport != None and self.transport.is_subway()
    
    def is_walk(self):
        return self.transport == None
    
    def is_land_transport(self):
        return self.transport != None and not self.transport.is_subway()
    
    def is_train(self):
        return self.transport != None and self.transport.is_train()
        
    def jsonable(self):
        return self.__dict__  
    
    def get_cost(self):
        result = 0
        # add price as-is
        if self.transport != None and self.transport.price != None:
            result += self.transport.price
        # add minutes * coefficient
        coef = 3
        if self.transport == None:
            coef = 2.5 # walking is nice
        elif self.is_land_transport() and not self.is_train():
            coef = 3.5 # land transport is not reliable
        result += self.duration * coef
        return result 
    
    def get_route_json(self):
        params = { 
                  'type': self.transport.type if self.transport != None else 'Walk', 
                  'start': self.start_location, 
                  'end': self.end_location,
                  'startIcon': self.start_icon,
                  'endIcon': self.end_icon,
                  'startName': self.start_name,
                  'endName': self.end_name
                 }
        return utils.to_json(params)
    
    def get_default_addinfo(self):
        addinfo = utils.duration_to_string(int(self.duration))
        if self.distance != None:
            addinfo += ', ' + utils.distance_to_string(self.distance)
        if self.transport != None and self.transport.price != None:
            addinfo += ', ' + utils.price_to_string(self.transport.price)
        if self.transport != None and self.transport.stops != None:
            addinfo += ', ' + utils.stops_to_string(self.transport.stops)
        if self.transport != None and self.transport.interval != None:
            addinfo += ', ' + _('runs every') + ' ' + utils.duration_to_string(self.transport.interval)
        return addinfo
        
# Class that represents a Transport        
class Transport(object):
    def __init__(self, transport_type, line_number = None, interval = None, price = None, stops = None):
        self.type = transport_type
        self.line_number = line_number
        self.interval = interval
        self.price = price
        self.stops = stops
        self.start_code = None
        self.end_code = None
        
    def is_subway(self):
        return self.type == 'Subway'
    
    def is_train(self):
        return self.type == 'Train'
    
    def jsonable(self):
        return self.__dict__
    
# Class that represents a Geo Point
class GeoPoint(object):
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng
        
    def to_url_param(self):
        return str(self.lat) + ',' + str(self.lng)
        
    def __str__(self):
        return "{ 'lat': " + str(self.lat) + ", 'lng': " + str(self.lng) + "}"
    
    def jsonable(self):
        return self.__dict__