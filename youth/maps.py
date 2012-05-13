#coding=utf-8

import json
import re
import urllib
from google.appengine.api import urlfetch
from lib.BeautifulSoup import BeautifulSoup
from youth import utils

# Class that represents a Route Step
class RouteStep(object):
    def __init__(self, direction = None, duration = None, addinfo = None, 
                 transport = None, start_location = None, end_location = None, points = None):
        self.direction = direction
        self.duration = duration
        self.addinfo = addinfo
        self.start_location = start_location 
        self.end_location = end_location
        self.points = points        
        self.transport = transport
        
    def is_subway(self):
        return self.transport != None and self.transport.is_subway()
        
    def jsonable(self):
        return self.__dict__   
        
# Class that represents a Transport        
class Transport(object):
    def __init__(self, transport_type, line_number, interval, price = None):
        self.type = transport_type
        self.line_number = line_number
        self.interval = interval
        self.price = price
        
    def is_subway(self):
        return self.type == 'Subway'
    
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
        
        

def get_route(from_addr, to_addr):
    transit = get_transit_route(from_addr, to_addr)
    first_subway = True
    for index in range(len(transit)):
        step = transit[index]
        previous_step = transit[index - 1] if index > 0 else None
        next_step = transit[index + 1] if index < len(transit) - 1 else None
        
        start = step.start_location 
        end = step.end_location
        
        
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
            
            # Add 3/4 of service interval duration
            if not step.transport.is_subway() and step.transport.interval != None:
                step.duration += step.transport.interval * 3 / 4 
                                        
        # Do not show the map for change walks inside subway
        elif step.transport == None and previous_step != None and next_step != None and \
            previous_step.transport.is_subway() and next_step.transport.is_subway():
            step.duration = 4 # subway change is 4 minutes
            step.addinfo = 'About ' + str(step.duration) + ' mins'
            
        # Subway step should be a direct line on the map
        if step.is_subway():
            step.points = [start, end]
        else:
            step.points = get_route_leg(str(start.lat) + ',' + str(start.lng), 
                                       str(end.lat) + ',' + str(end.lng),
                                       'walking' if step.transport != None else 'driving')            
            
    # Find all subways
    subways = [step for step in transit if step.transport != None and step.transport.is_subway()]
    if len(subways) > 0:
        # Add 4 minutes to exit subway
        subways[-1].direction += ', leave the subway'
        subways[-1].duration += 4            
        
    return transit

def get_route_leg(origin, destination, mode = 'walking'):
    route_points = []
    url = "http://maps.googleapis.com/maps/api/directions/json?origin=" + origin + "&destination=" + destination + "&sensor=false&mode=" + mode
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        route = json.loads(result.content)
        for leg in route['routes'][0]['legs']:
            for step in leg['steps']:
                if len(route_points) == 0:
                    route_points.append(GeoPoint(step['start_location']['lat'], step['start_location']['lng']));                
                route_points.append(GeoPoint(step['end_location']['lat'], step['end_location']['lng']));
    return route_points

def get_transit_route(from_addr, to_addr):
    # Make request to Google Transit
    url = "http://maps.google.com/?saddr=" + urllib.quote(from_addr) + "&daddr=" + urllib.quote(to_addr) + "&dirflg=r&output=json"
    result = urlfetch.fetch(url)
    response = result.content

    # Get points array    
    start_index = response.find(',points:[{') + 8
    end_index = response.find('}],', start_index) + 2
    points_string = response[start_index:end_index].decode('string-escape').replace('lat', '"lat"').replace('lng', '"lng"').replace('arrow', '"arrow"').replace('point', '"point"').replace('prevPoint', '"prevPoint"')
    points = eval(points_string)
    
    # Get steps array
    start_index = response.find(',steps:[{') + 7
    end_index = response.find('}],', start_index) + 2
    steps_string = response[start_index:end_index].decode('string-escape').replace('depPoint', '"depPoint"').replace('arrPoint', '"arrPoint"').replace('depMarker', '"depMarker"').replace('arrMarker', '"arrMarker"')
    steps = eval(steps_string)

    # Get route description HTML
    start_index = response.find(',panel:"') + 8
    end_index = response.find('",panelId:', start_index)
    html = response[start_index:end_index].decode("string-escape")
    
    # Parse the route
    route = parse(html, points, steps)
    return route
    
    
def parse(html, points, steps):    
    soup = BeautifulSoup(html)
    route0 = soup.find("div", { "id" : "ts_route_0" })
    directions = []
    for index in range(len(steps) - 1): 
        step_node = route0.find(attrs = { "id" : "step_0_" + str(index) + "_segment" })

        step = RouteStep()                
        
        if step_node != None:
            step.direction = get_node_text(step_node.find(attrs = { "class" : "dir-ts-direction" }))
            segment_text = get_nodes_text(step_node.findAll(attrs = { "class": "dirsegtext" }))
            if segment_text != '':
                step.direction += ': ' + segment_text
                 
            step.addinfo = get_nodes_text(step_node.findAll(attrs = { "class" : re.compile('^dir-ts-addinfo.*') })).replace('(','').replace(')','')            
            step.duration = parse_duration(step.addinfo)
            
            transport_type = get_transport(step.direction)
            if transport_type != None and transport_type != 'Walk':
                line_number = get_node_text(step_node.find(attrs = { "class" : "trtline" }))
                service_interval = parse_service_interval(step.addinfo)
                step.transport = Transport(transport_type, line_number, service_interval)                
                if not step.transport.is_subway(): 
                    step.direction = step.direction.replace(step.transport.type, step.transport.type + ' number ' + step.transport.line_number)            
            
            if step_node.nextSibling != None:
                    arrive_node = step_node.nextSibling.find(text = re.compile('^Arrive.*'))
                    if arrive_node != None:
                        step.direction += ' till ' + get_node_text(arrive_node.nextSibling)
            
        start_point = points[steps[index]['depPoint']]
        end_point = points[steps[index]['arrPoint']]
        
        step.start_location = GeoPoint(start_point['lat'], start_point['lng'])
        step.end_location = GeoPoint(end_point['lat'], end_point['lng'])
        
        directions.append(step)
  
    return directions

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
    if direction.find('Walk to') >= 0:
        return 'Walk'
    elif direction.find('Bus') >= 0:
        return 'Bus'
    elif direction.find('Share taxi') >= 0:
        return 'Share taxi'
    elif direction.find('Trolleybus') >= 0:
        return 'Trolleybus'
    elif direction.find('Subway') >= 0:
        return 'Subway'
    elif direction.find('Tram') >= 0:
        return 'Tram'
    
    return ''
    
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