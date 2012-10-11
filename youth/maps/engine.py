#coding=utf-8

import json
import re
import urllib
import logging
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from django.utils.translation import ugettext as _
from lib.BeautifulSoup import BeautifulSoup
from lib import geo
from lib import translit
from youth import utils
from youth.maps import router
from youth.maps import common
from youth.maps import rusavtobus
        

def get_walking_step(start_location, end_location, end_name = None):
    step = None
    direct_distance = estimate_distance(start_location, end_location)
    if direct_distance > 150:
        language = utils.get_language()
        params = { 
                  'origin': start_location.to_url_param(),
                  'destination': end_location.to_url_param(), 
                  'sensor' : 'false', 
                  'mode': 'walking',
                  'language' : language
                  }
        url = 'http://maps.google.com/maps/api/directions/json?' + urllib.urlencode(params)
        result = urlfetch.fetch(url)
    
        if result.status_code == 200:
            route = json.loads(result.content)
            if route['status'] == 'OVER_QUERY_LIMIT':
                logging.warn('OVER_QUERY_LIMIT while fetching walking directions')
            elif route['status'] == 'ZERO_RESULTS':
                # no route found
                pass
            else:
                instructions = []
                duration = 0
                distance = 0
                for leg in route['routes'][0]['legs']:
                    for leg_step in leg['steps']:
                        instructions.append(clean_walk_direction(utils.remove_html_tags(leg_step['html_instructions'])))
                        duration += int(leg_step['duration']['value'])
                        distance += int(leg_step['distance']['value'])
                step = common.RouteStep()                            
                step.direction = ', '.join(instructions)
                step.duration = int(duration / 60)      
                step.distance = distance                  
        else:
            logging.warn('Walking route failed: ' + str(result.status_code))
        
    if step == None: #google not needed or failed
        step = common.RouteStep()
        step.distance = estimate_distance(start_location, end_location) * 1.4
        step.duration = int(step.distance / 80 + 0.5)
        
    if end_name != None:
        walk_text = _('Walk to') + ' ' + end_name
        if step.direction != None:
            step.direction = walk_text + ': ' + step.direction
        else:
            step.direction = walk_text
    elif step.direction == None:
        step.direction = _('Walk') + ' ' + utils.distance_to_string(step.distance)

    step.transport = None # walk                
    step.start_location = start_location
    step.end_location = end_location
    step.has_map = True
    return step

def get_walking_route(start_location, end_location):
    step = get_walking_step(start_location, end_location, None)
    if step != None:
        return common.Route([step])
    
def get_subway_route(start_location, end_location):
    language = utils.get_language()
    route = router.get_route(start_location, end_location)
    if route == None:
        return None
    
    steps = []
            
    for leg in route:
        step = common.RouteStep()                                
        step.duration = int((sum([x.distance for x in leg.steps[1:]]) + 30) / 60)
        step.start_location = common.GeoPoint(leg.steps[0].station.lat, leg.steps[0].station.lng)
        step.end_location = common.GeoPoint(leg.steps[-1].station.lat, leg.steps[-1].station.lng)
        step.start_name = leg.steps[0].station.name if language != 'ru' else leg.steps[0].station.name_rus 
        step.end_name = leg.steps[-1].station.name if language != 'ru' else leg.steps[-1].station.name_rus
        step.transport = common.Transport(leg.transport, str(leg.line), stops = len(leg.steps) - 1)
        step.has_map = True
        steps.append(step)

    route = common.Route(steps)
    process_transit_route(start_location, end_location, route)
    if route.get_walk_duration() < 40:
        return route

def get_transit_route(start_location, end_location, engine = 'o', force = ''):
    language = utils.get_language()
    key = 'route_' + start_location.to_url_param() + '_' + end_location.to_url_param() + '_' + engine + '_' + language + '_' + force
    data = memcache.get(key) #@UndefinedVariable
    if data != None:
        return data
    
    distance = estimate_distance(start_location, end_location)
    if distance != None and distance < 2000:
        walk_route = get_walking_route(start_location, end_location)
        if walk_route != None and walk_route.get_duration() < 30:
            memcache.add(key, walk_route, 60*60) #@UndefinedVariable
            return walk_route
    
    subway_route = None
    if engine == 'o' or engine == 's':  
        subway_route = get_subway_route(start_location, end_location)
        if subway_route != None and distance > 5000:
            memcache.add(key, subway_route, 60*60) #@UndefinedVariable
            return subway_route
    
    routes = []
    if engine == 'o' or engine == 'r':
        routes = get_rusavtobus_routes(start_location, end_location)
    if engine == 'g' or routes is None or len(routes) == 0:
        routes = get_google_routes(start_location, end_location)
    if subway_route != None:
        routes.append(subway_route)
    if force.find('train') >= 0:
        routes_with_train = [x for x in routes if x.has_transport('Train')]
        if len(routes_with_train) > 0:
            routes = routes_with_train
    if force.find('nosharetaxi') >= 0:
        routes_without_sharetaxi = [x for x in routes if not x.has_transport('Share taxi')]
        if len(routes_without_sharetaxi) > 0:
            routes = routes_without_sharetaxi
    if len(routes) > 0:
        route_optimal = min(routes, key=lambda x: x.get_cost())
        memcache.add(key, route_optimal, 60*60) #@UndefinedVariable
        return route_optimal 

def get_rusavtobus_routes(start_location, end_location):
    routes = rusavtobus.get_routes(start_location, end_location)
    for route in routes:
        process_transit_route(start_location, end_location, route)
    return routes

def get_google_routes(start_location, end_location):
    # Make request to Google Transit
    url = "http://maps.google.com/?saddr=" + start_location.to_url_param() + "&daddr=" + end_location.to_url_param() + "&dirflg=r&output=json&time=10:00am"
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
        process_transit_route(start_location, end_location, route)
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
    
            step = common.RouteStep()                
            
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
                    step.transport = common.Transport(transport_type, line_number, step.service_interval)
                    step.direction = _(step.transport.type)
                    step.transport.stops = parse_stops(step.addinfo)                
                    if step.transport.is_subway(): 
                        step.direction += utils.subway_color(' ' + _('line') + ' ' + str(step.transport.line_number), step.transport.line_number);
                    else:
                        step.direction += ' ' + _('number') + ' ' + step.transport.line_number            
                        
                step.start_name = clean_walk_direction(get_node_text(step_node.find('b')))
                if step_node.nextSibling != None:
                    arrive_node = step_node.nextSibling.find(text = re.compile('^Arrive.*'))
                    if arrive_node != None:
                        step.end_name = clean_walk_direction(get_node_text(arrive_node.nextSibling))
                
            start_point = points[steps[index]['depPoint']]
            end_point = points[steps[index]['arrPoint']]
            
            step.start_location = common.GeoPoint(start_point['lat'], start_point['lng'])
            step.end_location = common.GeoPoint(end_point['lat'], end_point['lng'])
            
            if not step.is_walk():
                directions.append(step)
        routes.append(common.Route(directions, 'google'))
        route_index += 1
  
    return routes

def process_transit_route(start_location, end_location, route):    
    language = utils.get_language()
    
    # Add end walk
    end_walk = get_walking_step(route.directions[-1].end_location, end_location)
    if end_walk.duration > 0:
        route.directions.append(end_walk)
    
    first_subway = True
    index = 0
    while index < len(route.directions) and index < 100:
        step = route.directions[index]
        previous_step = route.directions[index - 1] if index > 0 else None
        next_step = route.directions[index + 1] if index < len(route.directions) - 1 else None
        
        if step.transport != None:
            if step.transport.is_train():
                station = router.resolve_name(step.start_name, 'Train', step.start_location)
                if station != None:
                    step.start_name = station.name_rus if language == 'ru' else station.name
                    step.transport.start_code = station.name_rus
                    step.start_location.lat = station.lat
                    step.start_location.lng = station.lng
                station = router.resolve_name(step.end_name, 'Train', step.end_location)
                if station != None:
                    step.end_name = station.name_rus if language == 'ru' else station.name
                    step.transport.end_code = station.name_rus
                    step.end_location.lat = station.lat
                    step.end_location.lng = station.lng

            if not step.transport.is_subway() or first_subway:
                from_location = previous_step.end_location if previous_step != None else start_location 
                tostop_walk = get_walking_step(from_location, step.start_location,
                                               _(step.transport.type).lower() + ' ' + _('stop') + ' ' + step.start_name)
                route.directions.insert(index, tostop_walk)
                index += 1
            
            if step.transport.is_train():
                new_step = common.RouteStep(_('Buy the train tickets to') + ' ' + step.end_name + ', ' + _('wait for the train'),
                                       15, '', common.Transport('Train', price = step.transport.price))                
                route.directions.insert(index, new_step)
                index += 1
                step.transport.price = None
            
            if step.transport.is_subway():
                if first_subway:
                    new_step = common.RouteStep(_('Enter subway station') + ' ' + utils.subway_color(step.start_name, step.transport.line_number) + ' (' + _('buy the tokens if needed') + ')',
                                          5, utils.duration_to_string(5) + ', ' + utils.price_to_string(27), common.Transport('Subway', price = 27))                
                else:
                    to_text = _('Change to') + ' ' + utils.subway_color(_('line') + ' ' + str(step.transport.line_number), step.transport.line_number) + ' ' + _('station') + ' ' + utils.subway_color(step.start_name, step.transport.line_number)
                    new_step = common.RouteStep(to_text, 4, utils.duration_to_string(4))
                route.directions.insert(index, new_step)
                index += 1
                step.transport.price = None
                first_subway = False
                if step.transport.stops == 0:
                    route.directions.remove(step)
                    continue
                                
            # Set price for land transport 
            if step.transport.type in ['Bus', 'Trolleybus', 'Tram']:
                step.transport.price = 23
            elif step.transport.type in ['Share taxi']:
                step.transport.price = 35
                
            # Make trolleybus less optimistic
            if step.transport.type == 'Trolleybus':
                step.duration *= 1.4
                            
            # Add 3/4 of service interval duration
            if not step.transport.is_subway():
                if step.transport.interval != None:
                    step.duration += step.transport.interval * 3 / 4                 
                else:
                    step.duration += get_default_service_interval(step.transport) * 3 / 4
                                        
        # Do not show the map for change walks inside subway
        if step.is_walk() and previous_step != None and next_step != None and \
            previous_step.is_subway() and next_step.is_subway():
            step.duration = 4 # subway change is 4 minutes
        else:
            step.has_map = step.start_location != None and step.end_location != None
            
        if step.transport != None:
            if step.is_subway():
                step.direction = _(step.transport.type) + ': ' + utils.subway_color(_('line') + ' ' + step.transport.line_number, step.transport.line_number) + \
                                 ' ' + _('to') + ' ' + utils.subway_color(step.end_name, step.transport.line_number)
            elif step.transport.is_train():
                step.direction = _(step.transport.type) + ' ' + _('to') + ' ' + step.end_name
            else:
                step.direction = _(step.transport.type) + ' ' + step.transport.line_number + ' ' + _('to') + ' ' + step.end_name 
            
        # Improve walk to direction 
        if step.is_walk() and next_step != None and not next_step.is_walk():
            stop_text = _('station') if next_step.is_subway() else _('stop')
            step.direction = step.direction.replace(_('Walk to') + ' ', _('Walk to') + ' ' + _(next_step.transport.type).lower() + ' ' + stop_text + ' ')
   
        index += 1
         
    # Find all subways
    subways = [step for step in route.directions if step.is_subway() and step.direction != None]
    if len(subways) > 0:
        # Add 4 minutes to exit subway
        subways[-1].direction += ', ' + _('leave the subway')
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
    elif direction.find('Train') >= 0:
        return 'Train'
    
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

def get_default_service_interval(transport):
    interval = 0
    if transport.type == 'Bus':
        interval = 12
    elif transport.type == 'Trolleybus' or transport.type == 'Tram':
        interval = 15
    elif transport.type == 'Share taxi':
        interval = 10
    alternatives = len(transport.line_number.split('or'))
    if alternatives < 2:
        return interval
    elif alternatives == 2:
        return interval * 3 / 4
    elif alternatives == 3:
        return interval * 2 / 3
    else:
        return interval / 2

def estimate_distance(start_location, end_location):
    return geo.haversine(start_location.lng, start_location.lat, end_location.lng, end_location.lat)
    
def clean_walk_direction(direction):
    language = utils.get_language()
    result = direction
    if language != 'ru':
        result = translit.translify(result) 
    return result.replace(_('/M10'), '').replace(_('/M18'), '')