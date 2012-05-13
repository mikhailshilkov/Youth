import datetime

from youth import itinerary
from youth import hotel
from youth import stuff
from youth import view

def do_home(request, response):
    view.to_html(None, 'home', response)

def do_itinerary(request, response):
    # get request parameters
    try: 
        start_time = datetime.datetime.strptime(request.get('time', '10:00'), '%H:%M')
    except:
        start_time = datetime.time(hour=10, minute=0)
    from_location = request.get('from', '59.945085,30.292699')
    view_mode = request.get('out', 'html')
    transport = request.get('transport', 'bus')

    # produce data        
    data = itinerary.get(from_location, start_time, transport)              
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'itinerary', response)
        
def do_hotel(request, response):
    # get request parameters        
    view_mode = request.get('out', 'html')
    
    # produce data        
    data = hotel.get()
    
    hotel.delete('Test 2')
    
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

def do_test(request, response):
    response.out.write(stuff.test())
    
def do_notfound(request, response):
    response.out.write('Page not found') #TODO: return a nice HTML with link to homepage