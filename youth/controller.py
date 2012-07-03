#coding=utf-8

import datetime

from youth import bot
from youth import itinerary
from youth import place
from youth import maps
from youth import stuff
from youth import view
from youth import param
from youth import router

def do_home(request, response):
    view.to_html(None, 'home', request, response)
    
def do_about(request, response):
    view.to_html(None, 'about', request, response)
    
def do_directions(request, response):
    # get request parameters
    start_time = get_start_time(request)
    view_mode = request.get('out', 'html')
    try:
        date = datetime.datetime.strptime(request.get('date', ''), '%Y-%m-%d')
    except:
        date = datetime.date.today() + datetime.timedelta(days=1)
        
    # get from and to (hotel name, attraction name or if not found - address)
    [from_place, from_location] = get_place(request, 'from', 'fll')
    [to_place, to_location] = get_place(request, 'to', 'tll')

    # produce data            
    data = itinerary.get_directions(from_place, from_location, to_place, to_location, date, start_time)              
    
    # populate the requested view
    if view_mode == 'none':
        view.empty(response);
    elif view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'directions', request, response)
        
def do_place(request, response):
    # get request parameters        
    view_mode = request.get('out', 'html')
    term = request.get('term', '')
    
    # produce data        
    data = place.get(term)
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'hotel', request, response)
        
def post_hotel(request):
    # get request parameters        
    name = request.get('name')
    address = request.get('address')
    lat = float(request.get('lat'))
    lng = float(request.get('lng'))
    place.add_hotel(name, address, lat, lng)
    
def delete_hotel(request):
    # get request parameters        
    name = request.get('name')
    place.delete_hotel(name)        

def post_attraction(request):
    # get request parameters        
    name = request.get('name')
    lat = float(request.get('lat'))
    lng = float(request.get('lng'))
    place.add_attraction(name, lat, lng)
    
def delete_attraction(request):
    # get request parameters        
    name = request.get('name')
    place.delete_attraction(name) 
        
def do_transit(request, response):
    # get request parameters
    from_location = maps.GeoPoint(*[float(x) for x in request.get('from').split(',')])
    to_location = maps.GeoPoint(*[float(x) for x in request.get('to').split(',')])    
    view_mode = request.get('out', 'html')

    # produce data        
    data = maps.get_transit_routes(from_location, to_location)
        
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'transit', request, response)    

def do_routing(request, response):
    # get request parameters
    from_location = maps.GeoPoint(*[float(x) for x in request.get('from').split(',')])
    to_location = maps.GeoPoint(*[float(x) for x in request.get('to').split(',')])    
    view_mode = request.get('out', 'html')

    # produce data        
    data = router.get_route(from_location, to_location)
        
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'routing', request, response)    
        
def do_train(request, response):
    # get request parameters
    view_mode = request.get('out', 'html')

    # produce data        
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    data = bot.fetch_trains('Санкт-Петербург', 'Новый Петергоф', tomorrow)
        
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'train', request, response)
        
def post_param(request, response):
    name = request.get('name')
    value = request.get('value')
    param.add(name, value)

def do_test(request, response):
    from google.appengine.tools import dev_appserver 
    dev_appserver.TearDownStubs()
    response.out.write(stuff.test())
    
def do_notfound(request, response):
    view.to_html(None, 'notfound', request, response)
    
def get_start_time(request):
    try: 
        start_time = datetime.datetime.strptime(request.get('time', '09-30'), '%H-%M').time()
    except:
        start_time = datetime.time(hour=10, minute=0)
    return start_time

def get_place(request, name_param, coord_param):
    name = request.get(name_param, '')
    if name != '':
        places = place.get(name)
        if len(places) > 0:
            return [places[0], maps.GeoPoint(places[0].latitude, places[0].longitude)]
        
    coord = request.get(coord_param, '').replace('-', ',')
    if coord != '':
        return [name if name != '' else coord, maps.GeoPoint(*[float(x) for x in coord.split(',')])]