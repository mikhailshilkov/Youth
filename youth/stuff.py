#coding=utf-8

import urllib
import re
from google.appengine.api import urlfetch
from lib.BeautifulSoup import BeautifulSoup
import json
from youth.maps import GeoPoint

def test():
    #saddr = urllib.quote('59.94474100000001,30.294258000000013')
    daddr = urllib.quote('59.86732529999999,30.261337499999968')
    saddr = urllib.quote("59.841864,30.318321")
    #daddr = urllib.quote("St. Petersburg Sadovaya 32")
    url = "http://maps.google.com/?saddr=" + saddr + "&daddr=" + daddr + "&dirflg=r&output=json&hl=en"
    result = urlfetch.fetch(url)
    response = result.content
    #return response
    
    points = []
    points_starts = [match.start() + 8 for match in re.finditer(re.escape(',points:[{'), response)]
    for start_index in points_starts:
        end_index = response.find('}],', start_index) + 2
        points_string = response[start_index:end_index].decode('string-escape').replace('lat', '"lat"').replace('lng', '"lng"').replace('arrow', '"arrow"').replace('point', '"point"').replace('prevPoint', '"prevPoint"')
        points.append(eval(points_string))
    
    steps = []
    steps_starts = [match.start() + 7 for match in re.finditer(re.escape(',steps:[{'), response)]
    for start_index in steps_starts:
        end_index = response.find('}],', start_index) + 2
        steps_string = response[start_index:end_index].decode('string-escape').replace('depPoint', '"depPoint"').replace('arrPoint', '"arrPoint"').replace('depMarker', '"depMarker"').replace('arrMarker', '"arrMarker"')
        steps.append(eval(steps_string))

    start_index = response.find(',panel:"') + 8
    end_index = response.find('",panelId:', start_index)
    html = response[start_index:end_index].decode("string-escape")
    routes = parse(html, points, steps)
    
    #return response
    #return html
    #return points
    #return points_string
    #return routes
    
    route_points = []
    origin = 'shavrova'
    destination = 'utochkina'
    mode = 'walking'
    url = "http://maps.googleapis.com/maps/api/directions/json?origin=" + origin + "&destination=" + destination + "&sensor=false&mode=" + mode
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        return result.content
        #for leg in route['routes'][0]['legs']:
         #   for step in leg['steps']:
          #      if len(route_points) == 0:
           #         route_points.append(GeoPoint(step['start_location']['lat'], step['start_location']['lng']));                
            #    route_points.append(GeoPoint(step['end_location']['lat'], step['end_location']['lng']));
    return route_points
    
    
def parse(html, points_arr, steps_arr):    
    soup = BeautifulSoup(html)
    routes = []
    route_index = 0
    while True:
        route_node = soup.find("div", { "id" : "ts_route_" + str(route_index) })
        if route_node == None:
            break;
        directions = []
        total_duration = 0
        steps = steps_arr[route_index]
        points = points_arr[route_index]
        for index in range(len(steps)): 
            step = route_node.find(attrs = { "id" : "step_" + str(route_index) + "_" + str(index) + "_segment" })
            
            direction = ''
            duration = ''
            addinfo = ''
            line_number = ''
            arrive =''
            addinfo_duration = ''
            
            if step != None:
                direction_node = step.find(attrs = { "class" : "dir-ts-direction" })
                if direction_node != None:
                    action_node = direction_node.find(attrs = { "class" : "action" })
                    location_node = direction_node.find(attrs = { "class" : "location" })
                    if action_node != None and location_node != None:
                        direction = str(action_node.text) + ' ' + str(location_node.text)
                    else:
                        direction = str(direction_node.renderContents())
                    if step.nextSibling != 'None':
                        arrive_node = step.nextSibling.find(text = re.compile('^Arrive.*'))
                        if arrive_node != None:
                            arrive = arrive_node.nextSibling.text
                addinfo_nodes = step.findAll(attrs = { "class" : re.compile('^dir-ts-addinfo.*') })
                addinfo = remove_html_tags(get_nodes_text(addinfo_nodes))
                addinfo_duration_m = re.search('Service runs every\s(\d+)\smin', addinfo)
                if addinfo_duration_m != None:
                    addinfo_duration = addinfo_duration_m.group(1) 
                duration = parse_duration(addinfo)
                total_duration += duration
                segtext_nodes = step.findAll(attrs = { "class": "dirsegtext" })
                direction += ', ' + get_nodes_text(segtext_nodes)
                line_number_node = step.find(attrs = { "class" : "trtline" })
                if line_number_node != None:
                    line_number = str(line_number_node.text)            
                
            start_point = points[steps[index]['depPoint']]
            end_point = points[steps[index]['arrPoint']]
            directions.append({
                               'direction': remove_html_tags(direction), 
                               'duration': duration,
                               'addinfo': addinfo,
                               'addinfo_duration': addinfo_duration,
                               'line_number' : line_number,
                               'arrive': arrive,
                               'start_location': { 'lat': start_point['lat'], 'lng': start_point['lng'] },
                               'end_location': { 'lat': end_point['lat'], 'lng': end_point['lng'] } 
                               })
        routes.append({'directions' : directions, 'total_duration': total_duration})
        route_index += 1
    return routes

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def get_nodes_text(nodes):
    text = ''
    for j in range(len(nodes)):
        if text != '':
            text += ', '
        text += str(nodes[j].renderContents())
    return decode_unicode_references(text)

def _callback(matches):
    sym_id = matches.group(1)
    try:
        return unichr(int(sym_id))
    except:
        return sym_id

def decode_unicode_references(data):
    return re.sub("&#(\d+)(;|(?=\s))", _callback, data)

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
    return int(tmp)