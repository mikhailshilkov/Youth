#coding=utf-8

import urllib
import json
import logging
from google.appengine.api import memcache
from xml.etree import ElementTree as etree
from django.utils.translation import ugettext as _
from lib import urlopener
from youth import utils
from youth.maps import common
  
def get_routes(start_location, end_location):  
    data = get_xml(start_location, end_location)
    if data == None:
        return None
    
    tree = etree.fromstring(data.encode('utf-8'))
    
    routes = []
    for route_element in tree.getchildren():        
        directions = []
        for step_element in route_element.getchildren():
            stops_elements = step_element.findall('p')
            if len(stops_elements) > 0:
                from_element = stops_elements[0]
                to_element = stops_elements[-1]
                
                step = common.RouteStep()   
                transport_code = step_element.attrib['wt']
                transport_type = 'Unknown'
                if transport_code == '6':
                    transport_type = 'Subway'
                elif transport_code == '5':
                    transport_type = 'Share taxi'
                elif transport_code == '4':
                    transport_type = 'Trolleybus'
                elif transport_code == '3':
                    transport_type = 'Tram'
                elif transport_code == '2':
                    transport_type = 'Bus'
                elif transport_code == '8':
                    transport_type = 'Train'
                else:
                    raise Exception('Unknown transport ' + transport_code)                
                price = int(step_element.attrib['c'])
                if transport_code == '6':
                    line_name = step_element.attrib['wn']
                    if line_name.find(_('Kirovsko-Viborgskaya')) >= 0:
                        line_numbers = '1'
                    elif line_name.find(_('Moskovsko-Petrogradskaya')) >= 0:
                        line_numbers = '2'
                    elif line_name.find(_('Nevsko-Vasileostrovskaya')) >= 0:
                        line_numbers = '3'
                    elif line_name.find(_('Pravoberezhnaya')) >= 0:
                        line_numbers = '4'
                    elif line_name.find(_('Frunzensko-Primorskaya')) >= 0:
                        line_numbers = '5'
                    else:
                        raise Exception('Unknown subway line ' + line_name)
                else:
                    line_numbers = [y[1].split('_')[0] for y in [x.split(':') for x in step_element.attrib['wn'].split(';')] if y[0] == transport_code][0].replace(',', ' ' + _('or') + ' ')                
                step.duration = int(step_element.attrib['t'])
                step.start_location = common.GeoPoint(float(from_element.attrib['lat']), float(from_element.attrib['lng']))
                step.end_location = common.GeoPoint(float(to_element.attrib['lat']), float(to_element.attrib['lng']))
                step.transport = common.Transport(transport_type, line_numbers, price = price, stops = len(stops_elements) - 1)
                step.start_name = from_element.attrib['n']
                step.end_name = to_element.attrib['n']
                directions.append(step)
        
        if len(directions) > 0:
            routes.append(common.Route(directions, 'rusavtobus'))
            
    return routes

    
def get_xml(start_location, end_location):
    data = load(start_location, end_location)
    result = json.loads(data)
    if result['type'] == 'success':
        return result['xml']
    
def load(start_location, end_location):
    language = utils.get_language()
    key = 'rusbus_' + start_location.to_url_param() + '_' + end_location.to_url_param() + '_' + language
    data = memcache.get(key) #@UndefinedVariable
    if data != None:
        return data
    
    existing_cookie_used = True
    cookie_key = 'rusbus_cookie'
    cookie_header = memcache.get(cookie_key) #@UndefinedVariable
    opener = urlopener.URLOpener('spb.rusavtobus.ru', cookie_header)
    if cookie_header is None:
        logging.info('RusAvtobus: starting session')
        start_session(opener)
        existing_cookie_used = False
        
    data = retrieve(opener, start_location, end_location, language, key)
    if data is None and existing_cookie_used:
        # existing cookie might have expired, try with new one
        logging.warn('RusAvtobus: existing session expired, starting new session')
        existing_cookie_used = False
        opener = urlopener.URLOpener('spb.rusavtobus.ru')
        start_session(opener)
        data = retrieve(opener, start_location, end_location, language, key)
        
    if data is not None and not existing_cookie_used:
        memcache.add(cookie_key, opener.cookie_header, 60*60) #@UndefinedVariable
        
    if data is None:
        logging.error('RusAvtobus did not retrieve data')
    else:
        memcache.add(key, data) #@UndefinedVariable
        
    return data

def start_session(opener):
    #opener.open( 'http://spb.rusavtobus.ru')
    data = {
            'map': '0'
    }
    form_data = urllib.urlencode(data)
    opener.open('http://spb.rusavtobus.ru/modules/interface/interface.action.php', form_data)
      
def retrieve(opener, start_location, end_location, language, key):  
    data = {
     'rad': '400',
     'target': 'summary',
     'types': '8',
     'alat': str(start_location.lat),
     'alng': str(start_location.lng),
     'blat': str(end_location.lat),
     'blng': str(end_location.lng),
     'srt': '0',
     'showtraf': '0',
     'timetraf': '0',
     'mode': 'intime',
     'stime': '1;09:30',
     'cityid': '2',
     'lang': language
    }
    form_data = urllib.urlencode(data)
    result = opener.open('http://spb.rusavtobus.ru/modules/search/loaders/mainroute.loader.php', form_data)
    if len(result.content) > 0:    
        memcache.add(key, result.content, 60*60) #@UndefinedVariable
        return result.content
