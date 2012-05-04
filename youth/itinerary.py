#coding=utf-8

from youth import utils
from youth import maps

def get(from_location, start_time, transport):
    if transport == 'meteor':
        title_to = 'Way to Peterhof: Meteor (speed boat)'
        summary_to = 'Expenses: 95 RUR, travel time: 1h15'
        route = maps.get_route(from_location, '59.93993,30.309073')
        steps_to = get_steps(route, start_time)
    elif transport == 'train':
        title_to = 'Way to Peterhof: subway + suburban train'
        summary_to = 'Expenses: 95 RUR, travel time: 1h55'
        route = maps.get_route(from_location, '59.9072128,30.299578099999962')
        steps_to = get_steps(route, start_time)
    elif transport == 'bus':
        title_to = 'Way to Peterhof: subway + bus'
        summary_to = 'Expenses: 95 RUR, travel time: 2h00'
        route = maps.get_route(from_location, '59.86732529999999,30.261337499999968')
        route.append({
                       'direction': 'Leave the subway, cross the street through the underpass and find a bus stop', 
                       'duration': 5,
                       'addinfo': 'About 5 mins, 150 m',
                       'transport': { 'type': 'walk' },
                       'start_location': { 'lat': 59.86758, 'lng': 30.261308 },
                       'end_location': { 'lat': 59.868398, 'lng': 30.259806 },
                       'points' : maps.get_route_leg('59.86758,30.261308', '59.868398,30.259806')
                     })
        route.append({
                       'direction': 'Take a minibus ("route-taxi"). Look for one of the following route numbers: К-424, ' +
                            'K-424a, К-300, К-224, К-401a, К-404 or any route-taxi where you see word "Фонтаны" ' + 
                            'on the window. Pay to driver, price may slightly vary. You should ask driver to stop in Petrodhof.', 
                       'duration': 60,
                       'addinfo': 'About 1 hour, pay fare 70 RUR',
                       'transport': { 'type': 'sharetaxi' }
                     })
        route.append({
                       'direction': 'Leave route taxi on Pravlentskaya ulitsa and go to Lower Park entry', 
                       'duration': 10,
                       'addinfo': 'About 10 mins, 800 m',
                       'transport': { 'type': 'walk' },
                       'start_location': { 'lat': 59.883884, 'lng': 29.911548 },
                       'end_location': { 'lat': 59.880511, 'lng': 29.906809 },
                       'points' : maps.get_route_leg('59.883884,29.911548', '59.880511,29.906809')
                     })            
        steps_to = get_steps(route, start_time)

    else:                
        title_to = 'Unknown'
        summary_to = 'Unknown'
        steps_to = []
            
    trip_to = {'title': title_to,
               'summary': summary_to,
               'change_action': 'Change transport',
               'steps': steps_to}
    
    steps_in = [
        {'instruction': 'Buy the Lower Park tickets in a box office.' + 
                        'Our recommendation to visit Lower park and Upper park with all fountains at least. Also you can try to visit Grand palace you should be prepared to the huge queues. First one to buy tickets and another one to enter. Note that ticket in lower park works only for one visit. If you leave park you are not able to visit it again at the same day.',
         'start_time': utils.time_to_string(utils.time_add_mins(start_time, 120)),
         'hint' : 'pay fare: XXX RUR'}]
    trip_in = {'title': 'Peterhof sightseeing',
               'summary': 'Summary to be done',
               'steps': steps_in}
    
    option_bus = {'alias': 'bus',
                  'title': 'Subway + bus',
                  'time': '2h00',
                  'experience': 'Poor',
                  'onfoot': '1,300 m',
                  'price': '95 RUR per person',
                  'simplicity': 'Average',
                  'icon': 'placeholder',
                  'selected': transport == 'bus'}
    option_meteor = {'alias': 'meteor',
                  'title': 'Meteor (speed boat)',
                  'time': '1h15',
                  'experience': 'Good',
                  'onfoot': '900 m',
                  'price': '525 RUR per person',
                  'simplicity': 'Easy',
                  'icon': 'placeholder',
                  'risks': 'Risks: long queue before getting onboard',
                  'selected': transport == 'meteor'}
    option_train = {'alias': 'train',
                  'title': 'Subway + suburban train',
                  'time': '1h55',
                  'experience': 'Poor',
                  'onfoot': '2,500 m',
                  'price': '85 RUR per person',
                  'simplicity': 'Difficult',
                  'icon': 'placeholder',
                  'selected': transport == 'train'}
    
    context = { 'from_location': from_location, 'start_time' : utils.time_serialize(start_time) }
        
    return {'trips': [trip_to, trip_in], 'options': [option_bus, option_meteor, option_train], 'context': context}

def get_steps(route, start_time):    
    steps_to = []
    duration = 0
    for step in route: 
        steps_to.append({'instruction': step['direction'],
                 'start_time': utils.time_to_string(utils.time_add_mins(start_time, duration)),
                 'hint' : step['addinfo'],
                 'details' :
                 {
                    'show_label': 'Show the map',
                    'hide_label': 'Hide the map',
                    'action': 'map',
                    'map': { 'points' : step['points'] }
                 } if 'points' in step else None})
        duration += step['duration']
    return steps_to