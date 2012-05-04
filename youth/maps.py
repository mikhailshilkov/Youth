#coding=utf-8

import json
import re
import urllib

from google.appengine.api import urlfetch

from lib.BeautifulSoup import BeautifulSoup

def get_route(from_addr, to_addr):
    transit = get_transit_route(from_addr, to_addr)
    for step in transit: 
        start = step['start_location'] 
        end = step['end_location']
        transport_type = step['transport']['type']
        if transport_type == 'subway':
            step['points'] = [start, end]
        else:
            step['points'] = get_route_leg(str(start['lat']) + ',' + str(start['lng']), 
                                           str(end['lat']) + ',' + str(end['lng']),
                                           'walking' if transport_type == 'walk' else 'driving')
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
                    route_points.append(create_point(step['start_location']));                
                route_points.append(create_point(step['end_location']));
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
        
        direction = ''
        duration = ''
        addinfo = ''
        line_number = ''
        
        if step_node != None:
            direction = get_node_text(step_node.find(attrs = { "class" : "dir-ts-direction" }))
            addinfo = get_nodes_text(step_node.findAll(attrs = { "class" : re.compile('^dir-ts-addinfo.*') }))
            duration = parse_duration(addinfo)
            segment_text = get_nodes_text(step_node.findAll(attrs = { "class": "dirsegtext" }))
            if segment_text != '':
                direction += ': ' + segment_text 
            line_number = get_node_text(step_node.find(attrs = { "class" : "trtline" }))
            
        start_point = points[steps[index]['depPoint']]
        end_point = points[steps[index]['arrPoint']]
        directions.append({
                           'direction': direction, 
                           'duration': duration,
                           'addinfo': addinfo.replace('(', '').replace(')', ''),
                           'transport': 
                            {
                             'type': get_transport(direction),
                             'line_number' : line_number
                            },
                           'start_location': { 'lat': start_point['lat'], 'lng': start_point['lng'] },
                           'end_location': { 'lat': end_point['lat'], 'lng': end_point['lng'] } 
                           })    
    return directions

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def get_node_text(node):
    if node != None:
        return remove_html_tags(decode_unicode_references(str(node.renderContents()).strip()))
    return ''

def get_nodes_text(nodes):
    text = ''
    for j in range(len(nodes)):
        if text != '':
            text += ', '
        text += remove_html_tags(decode_unicode_references(str(nodes[j].renderContents())))
    return text

def get_transport(direction):
    if direction.find('Walk to') >= 0:
        return 'walk'
    elif direction.find('Share taxi') >= 0:
        return 'share_taxi'
    elif direction.find('Trolleybus') >= 0:
        return 'trolleybus'
    elif direction.find('Subway') >= 0:
        return 'subway'
    
    return ''

def _callback(matches):
    sym_id = matches.group(1)
    try:
        return unichr(int(sym_id))
    except:
        return sym_id

def decode_unicode_references(data):
    return re.sub("&#(\d+)(;|(?=\s))", _callback, data)
    
def create_point(point):
    return { 'lat': point['lat'], 'lng': point['lng'] }

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