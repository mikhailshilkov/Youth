#coding=utf-8

import json
import re
import urllib
import logging
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from lib.BeautifulSoup import BeautifulSoup
from lib import geo
from youth import utils
from youth import router

# Class that represents a Route
class Route(object):
    def __init__(self, directions):
        self.directions = directions
        
    def get_duration(self):
        return sum([step.duration for step in self.directions])
    
    def get_cost(self):
        return sum([step.get_cost() for step in self.directions])

# Class that represents a Route Step
class RouteStep(object):
    def __init__(self, direction = None, duration = None, addinfo = None, 
                 transport = None, start_location = None, end_location = None, 
                 has_map = False, hint = None):
        self.direction = direction
        self.duration = duration
        self.addinfo = addinfo
        self.start_location = start_location 
        self.end_location = end_location
        self.transport = transport
        self.has_map = has_map
        self.hint = hint
        self.start_icon = None
        self.end_icon = None
        
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
        elif self.is_land_transport():
            coef = 3.5 # land transport is not reliable
        result += self.duration * coef
        return result 
    
    def get_route_json(self):
        params = { 
                  'type': self.transport.type if self.transport != None else 'Walk', 
                  'start': self.start_location, 
                  'end': self.end_location,
                  'startIcon': self.start_icon,
                  'endIcon': self.end_icon 
                 }
        return utils.to_json(params)
        
# Class that represents a Transport        
class Transport(object):
    def __init__(self, transport_type, line_number = None, interval = None, price = None, stops = None):
        self.type = transport_type
        self.line_number = line_number
        self.interval = interval
        self.price = price
        self.stops = stops
        
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
        
    def __str__(self):
        return "{ 'lat': " + str(self.lat) + ", 'lng': " + str(self.lng) + "}"
    
    def jsonable(self):
        return self.__dict__
        

def get_walking_route(origin, destination):
    params = { 
              'origin': origin,
              'destination': destination, 
              'sensor' : 'false', 
              'mode': 'walking'
              }
    url = 'http://maps.google.com/maps/api/directions/json?' + urllib.urlencode(params)
    result = urlfetch.fetch(url)
    
    if result.status_code == 200:
        route = json.loads(result.content)
        if route['status'] == 'OVER_QUERY_LIMIT':
            logging.warn('OVER_QUERY_LIMIT while fetching walking directions')
            return None # Google refuses to work
        
        instructions = []
        duration = 0
        distance = 0
        start_location = None
        for leg in route['routes'][0]['legs']:
            for leg_step in leg['steps']:
                instructions.append(utils.remove_html_tags(leg_step['html_instructions']))
                duration += int(leg_step['duration']['value'])
                distance += int(leg_step['distance']['value'])
                if start_location == None:
                    start_location = GeoPoint(leg_step['start_location']['lat'], leg_step['start_location']['lng'])
                end_location = GeoPoint(leg_step['end_location']['lat'], leg_step['end_location']['lng'])
        step = RouteStep()                            
        step.direction = ', '.join(instructions)
        step.duration = duration / 60
        step.addinfo = 'About ' + str(step.duration)  + ' mins, ' + str(distance) + ' m'
        step.transport = None # walk                
        step.start_location = start_location
        step.end_location = end_location
        step.has_map = True
        return Route([step])

def get_subway_route(origin, destination):
    route = router.get_route(origin, destination)

    steps = []
    start_location = GeoPoint(route[0]['node'].lat, route[0]['node'].lng)
        
    duration = 5
    step = RouteStep('Enter subway station ' + route[0]['node'].name,
                     duration, 'About ' + str(duration)  + ' mins', Transport('Subway', price = 27),
                     start_location)
    steps.append(step)
    
    for index in range(len(route)):
        route_step = route[index]
        line = route_step['node'].line
        last_station = index == len(route) - 1
        duration += route_step['distance']
        if last_station or route[index+1]['node'].line != line:
            if index > 0: # The change might be the first move => don't add a 0 stations way
                step = RouteStep()                                
                step.direction = 'Subway line ' + str(line) + ' to ' + str(route_step['node'].name)
                step.duration = duration / 60
                step.addinfo = 'About ' + str(step.duration)  + ' mins'
                step.transport = Transport('Subway')
                step.start_location = start_location
                step.end_location = GeoPoint(route_step['node'].lat, route_step['node'].lng) 
                step.has_map = True
                steps.append(step)
                duration = 0
            if not last_station:
                step = RouteStep('Change to subway station ' + route[index+1]['node'].name + ', line ' + str(route[index+1]['node'].line),
                                 route_step['distance'] / 60, 'About ' + str(step.duration)  + ' mins')
                steps.append(step)
                start_location = GeoPoint(route[index+1]['node'].lat, route[index+1]['node'].lng)                
    
    start_walk = get_walking_route(origin, str(steps[0].start_location.lat) + ',' + str(steps[0].start_location.lng))
    steps.insert(0, start_walk.directions[0])
            
    end_walk = get_walking_route(str(steps[-1].end_location.lat) + ',' + str(steps[-1].end_location.lng), destination)
    steps.append(end_walk.directions[0])
                
    if start_walk.get_duration() + end_walk.get_duration() < 40:
        return Route(steps)

def get_transit_route(from_addr, to_addr):
    key = 'route_' + from_addr + '_' + to_addr
    data = memcache.get(key) #@UndefinedVariable
    if data != None:
        pass#return data
    
    distance = estimate_distance(from_addr, to_addr)
    if distance != None and distance < 2000:
        walk_route = get_walking_route(from_addr, to_addr)
        if walk_route != None and walk_route.get_duration() < 30:
            memcache.add(key, walk_route, 60*60) #@UndefinedVariable
            return walk_route
        
    subway_route = get_subway_route(from_addr, to_addr)
    if subway_route != None:
        memcache.add(key, subway_route, 60*60) #@UndefinedVariable
        return subway_route
    
    routes = get_transit_routes(from_addr, to_addr)
    route_optimal = min(routes, key=lambda x: x.get_cost())
    memcache.add(key, route_optimal, 60*60) #@UndefinedVariable
    return route_optimal    

def get_transit_routes(from_addr, to_addr):
    # Make request to Google Transit
    url = "http://maps.google.com/?saddr=" + urllib.quote(from_addr) + "&daddr=" + urllib.quote(to_addr) + "&dirflg=r&output=json&time=10:00am"
    result = urlfetch.fetch(url)
    response = result.content
    
    # Get points arrays    
    points = []
    points_starts = [match.start() + 8 for match in re.finditer(re.escape(',points:[{'), response)]
    for start_index in points_starts:
        end_index = response.find('}],', start_index) + 2
        points_string = response[start_index:end_index].decode('string-escape').replace('lat', '"lat"').replace('lng', '"lng"').replace('arrow', '"arrow"').replace('point', '"point"').replace('prevPoint', '"prevPoint"')
        points.append(eval(points_string))
    
    # Get steps arrays
    steps = []
    steps_starts = [match.start() + 7 for match in re.finditer(re.escape(',steps:[{'), response)]
    for start_index in steps_starts:
        end_index = response.find('}],', start_index) + 2
        steps_string = response[start_index:end_index].decode('string-escape').replace('depPoint', '"depPoint"').replace('arrPoint', '"arrPoint"').replace('depMarker', '"depMarker"').replace('arrMarker', '"arrMarker"')
        steps.append(eval(steps_string))

    # Get route description HTML
    start_index = response.find(',panel:"') + 8
    end_index = response.find('",panelId:', start_index)
    html = response[start_index:end_index].decode("string-escape")
    
    # Parse the routes
    routes = parse(html, points, steps)
    for route in routes:
        process_transit_route(route)
    return routes
    
def parse(html, points_array, steps_array):    
    soup = BeautifulSoup(html)
    routes = []
    route_index = 0
    while True:
        route_node = soup.find("div", { "id" : "ts_route_" + str(route_index) })
        if route_node == None:
            break;
        directions = []
        total_duration = 0
        steps = steps_array[route_index]
        points = points_array[route_index]
        for index in range(len(steps) - 1): 
            step_node = route_node.find(attrs = { "id" : "step_" + str(route_index) + "_" + str(index) + "_segment" })
    
            step = RouteStep()                
            
            if step_node != None:
                step.direction = get_node_text(step_node.find(attrs = { "class" : "dir-ts-direction" }))
                segment_text = get_nodes_text(step_node.findAll(attrs = { "class": "dirsegtext" }))                
                if segment_text != '':
                    if step.direction.find('Unknown') > 0: # Prevent 'Walk to Unknown' direction
                        step.direction = segment_text
                    else:
                        step.direction += ': ' + segment_text
                     
                step.addinfo = get_nodes_text(step_node.findAll(attrs = { "class" : re.compile('^dir-ts-addinfo.*') })).replace('(','').replace(')','')
                step.duration = parse_duration(step.addinfo)
                step.initial_duration = step.duration
                total_duration += step.duration
                
                transport_type = get_transport(step.direction)
                if transport_type == None or transport_type == 'Walk':
                    step.direction = clean_walk_direction(step.direction)
                else:
                    line_number = get_node_text(step_node.find(attrs = { "class" : "trtline" }))
                    step.service_interval = parse_service_interval(step.addinfo)
                    if step.service_interval == None:
                        step.service_interval = get_default_service_interval(transport_type) 
                    step.transport = Transport(transport_type, line_number, step.service_interval)
                    step.direction = step.transport.type
                    step.transport.stops = parse_stops(step.addinfo)                
                    if step.transport.is_subway(): 
                        step.direction += ' line ' + step.transport.line_number
                    else:
                        step.direction += ' number ' + step.transport.line_number            
                
                if step_node.nextSibling != None:
                        arrive_node = step_node.nextSibling.find(text = re.compile('^Arrive.*'))
                        if arrive_node != None:
                            step.direction += ' to ' + get_node_text(arrive_node.nextSibling)
                
            start_point = points[steps[index]['depPoint']]
            end_point = points[steps[index]['arrPoint']]
            
            step.start_location = GeoPoint(start_point['lat'], start_point['lng'])
            step.end_location = GeoPoint(end_point['lat'], end_point['lng'])
            
            directions.append(step)
        routes.append(Route(directions))
        route_index += 1
  
    return routes

def process_transit_route(transit):
    first_subway = True
    for index in range(len(transit.directions)):
        step = transit.directions[index]
        previous_step = transit.directions[index - 1] if index > 0 else None
        next_step = transit.directions[index + 1] if index < len(transit.directions) - 1 else None
        
        if step.transport != None:
            # Calculate step expenses
            if step.transport.is_subway() and first_subway:
                step.transport.price = 25
                previous_step.duration += 5
                previous_step.addinfo = 'About ' + str(previous_step.duration) + ' mins' 
                first_subway = False
            elif step.transport.type in ['Bus', 'Trolleybus', 'Tram']:
                step.transport.price = 21
            elif step.transport.type in ['Share taxi']:
                step.transport.price = 30
                
            # Make trolleybus less optimistic
            if step.transport.type == 'Trolleybus':
                step.duration *= 1.4
            
            # Create manual description
            step.addinfo = 'About ' + str(int(step.duration)) + ' mins'
            if step.transport.stops != None:
                step.addinfo += ', ' + str(step.transport.stops) + ' stops'
                
            # Add 3/4 of service interval duration
            if not step.transport.is_subway() and step.transport.interval != None:
                step.duration += step.transport.interval * 3 / 4                 
                step.addinfo += ', runs every ' + str(step.transport.interval) + ' mins'
                                        
        # Do not show the map for change walks inside subway
        if step.is_walk() and previous_step != None and next_step != None and \
            previous_step.is_subway() and next_step.is_subway():
            step.duration = 4 # subway change is 4 minutes
            step.addinfo = 'About ' + str(step.duration) + ' mins'
        else:
            step.has_map = step.start_location != None and step.end_location != None
            
        # Improve walk to direction 
        if step.is_walk() and next_step != None and not next_step.is_walk():
            stop_text = 'station' if next_step.is_subway() else 'stop'
            step.direction = step.direction.replace('Walk to ', 'Walk to ' + next_step.transport.type.lower() + ' ' + stop_text + ' ')
            
    # Find all subways
    subways = [step for step in transit.directions if step.transport != None and step.transport.is_subway()]
    if len(subways) > 0:
        # Add 4 minutes to exit subway
        subways[-1].direction += ', leave the subway'
        subways[-1].duration += 4

def get_node_text(node):
    if node != None:
        return utils.remove_html_tags(utils.decode_unicode_references(str(node.renderContents()).strip()))
    return ''

def get_nodes_text(nodes):
    text = ''
    for j in range(len(nodes)):
        if text != '':
            text += ', '
        text += utils.remove_html_tags(utils.decode_unicode_references(str(nodes[j].renderContents())))
    return text

def get_transport(direction):
    if direction.find('Bus') >= 0:
        return 'Bus'
    elif direction.find('Share taxi') >= 0:
        return 'Share taxi'
    elif direction.find('Trolleybus') >= 0:
        return 'Trolleybus'
    elif direction.find('Subway') >= 0:
        return 'Subway'
    elif direction.find('Tram') >= 0:
        return 'Tram'
    
    return 'Walk'
    
def parse_duration(info):
    tmp = info
    # remove all text after the comma
    comma_index = tmp.find(',')
    if comma_index > 0:
        tmp = info[0:comma_index] 
    # remove 'About', '(', ' mins'
    tmp = tmp.replace('About ', '')
    tmp = tmp.replace('(', '')
    tmp = tmp.replace(' mins', '')
    tmp = tmp.replace(' min', '')
    try:
        return int(tmp)
    except ValueError:
        return 0

def parse_service_interval(info):
    regex_match = re.search('Service runs every\s(\d+)\smin', info)
    if regex_match != None:
        return int(regex_match.group(1))
    return None

def parse_stops(info):
    regex_match = re.search(',\s(\d+)\sstop', info)
    if regex_match != None:
        return int(regex_match.group(1))
    return None

def get_default_service_interval(transport_type):
    if transport_type == 'Bus':
        return 12
    elif transport_type == 'Trolleybus':
        return 15
    elif transport_type == 'Share taxi':
        return 10
    return 0

def estimate_distance(from_addr, to_addr):
    try:
        from_coord = from_addr.split(',')
        to_coord = to_addr.split(',')
        return geo.haversine(float(from_coord[0]), float(from_coord[1]), float(to_coord[0]), float(to_coord[1]))
    except:
        return None
    
def clean_walk_direction(direction):
    return direction.replace('/M10', '')