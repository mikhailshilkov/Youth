#coding=utf-8

import datetime

from youth import bot
from youth import itinerary
from youth import hotel
from youth import attraction
from youth import maps
from youth import stuff
from youth import utils
from youth import view

def do_home(request, response):
    view.to_html(None, 'home', response)
    
def get_start_time(request):
    try: 
        start_time = datetime.datetime.strptime(request.get('time', '10-00'), '%H-%M').time()
    except:
        start_time = datetime.time(hour=10, minute=0)
    return start_time

def do_directions(request, response):
    # get request parameters
    start_time = get_start_time(request)
    from_address = request.get('address', '')
    from_location = request.get('from', '59.945085-30.292699').replace('-', ',')
    attraction = request.get('attraction', '')
    to_location = request.get('to', '59.945085-30.292699').replace('-', ',')
    view_mode = request.get('out', 'html')
    try:
        date = datetime.datetime.strptime(request.get('date', ''), '%Y-%m-%d')
    except:
        date = datetime.date.today() + datetime.timedelta(days=1)

    # produce data        
    data = itinerary.get_directions(from_address, from_location, attraction, to_location, date, start_time)              
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'directions', response)


def do_itinerary(request, response):
    # get request parameters
    start_time = get_start_time(request)
    from_location = request.get('from', '59.945085-30.292699').replace('-', ',')
    view_mode = request.get('out', 'html')
    transport = request.get('transport', 'bus')
    address = request.get('address', from_location)
    try:
        date = datetime.datetime.strptime(request.get('date', ''), '%Y-%m-%d')
    except:
        date = datetime.date.today() + datetime.timedelta(days=1)

    # produce data        
    data = { 
            'from_location': from_location,
            'address': address,
            'date': utils.date_serialize(date), 
            'time' : utils.time_serialize(start_time),
            'transport': transport 
           }              
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'itinerary', response)

def do_itinerary_trip(request, response):
    # get request parameters
    start_time = get_start_time(request)
    from_location = request.get('from', '59.945085-30.292699').replace('-', ',')
    view_mode = request.get('out', 'html')
    transport = request.get('transport', 'bus')
    try:
        date = datetime.datetime.strptime(request.get('date', ''), '%Y-%m-%d')
    except:
        date = datetime.date.today() + datetime.timedelta(days=1)

    # produce data        
    data = itinerary.get_trip(from_location, date, start_time, transport)              
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'trip', response)

def do_itinerary_options(request, response):
    # get request parameters
    start_time = get_start_time(request)
    from_location = request.get('from', '59.945085-30.292699').replace('-', ',')
    view_mode = request.get('out', 'html')
    try:
        date = datetime.datetime.strptime(request.get('date', ''), '%Y-%m-%d')
    except:
        date = datetime.date.today() + datetime.timedelta(days=1)

    # produce data        
    data = itinerary.get_options(from_location, date, start_time)              
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'itineraryOptions', response)
        
def do_hotel(request, response):
    # get request parameters        
    view_mode = request.get('out', 'html')
    term = request.get('term', '')
    
    # produce data        
    data = hotel.get(term)
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'hotel', response)
        
def post_hotel(request):
    # get request parameters        
    name = request.get('name')
    address = request.get('address')
    lat = float(request.get('lat'))
    lng = float(request.get('lng'))
    hotel.add(name, address, lat, lng)
    
def delete_hotel(request):
    # get request parameters        
    name = request.get('name')
    hotel.delete(name)        

def do_attraction(request, response):
    # get request parameters        
    view_mode = request.get('out', 'html')
    term = request.get('term', '')
    
    # produce data        
    data = attraction.get(term)
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'attraction', response)
        
def post_attraction(request):
    # get request parameters        
    name = request.get('name')
    lat = float(request.get('lat'))
    lng = float(request.get('lng'))
    attraction.add(name, lat, lng)
    
def delete_attraction(request):
    # get request parameters        
    name = request.get('name')
    attraction.delete(name) 
        
def do_transit(request, response):
    # get request parameters
    from_location = request.get('from', '59.945085,30.292699')
    view_mode = request.get('out', 'html')

    # produce data        
    data = maps.get_transit_routes(from_location, '59.86732529999999,30.261337499999968')
        
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'transit', response)    
        
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
        view.to_html(data, 'train', response)

def do_test(request, response):
    from google.appengine.tools import dev_appserver 
    dev_appserver.TearDownStubs()
    response.out.write(stuff.test())
    
def do_notfound(request, response):
    response.out.write('Page not found') #TODO: return a nice HTML with link to homepage