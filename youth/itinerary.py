#coding=utf-8

from youth import utils
from youth import maps

def get(start_time, transport):
    if transport == 'meteor':
        title_to = 'Way to Peterhof: Meteor (speed boat)'
        summary_to = 'Expenses: 95 RUR, travel time: 1h15'
        route = maps.get_transit_route('59.945085,30.292699', '59.93993,30.309073')
        steps_to = []
        duration = 0
        for step in route: 
            start = step['start_location'] 
            end = step['end_location']
            steps_to.append({'instruction': step['direction'],
                     'start_time': utils.time_to_string(utils.time_add_mins(start_time, duration)),
                     'hint' : step['addinfo'],
                     'details' :
                     {
                        'show_label': 'Show the map',
                        'hide_label': 'Hide the map',
                        'action': 'map',
                        'map': { 'points' : maps.get_route(str(start['lat']) + ',' + str(start['lng']), 
                                                           str(end['lat']) + ',' + str(end['lng']),
                                                           'walking' if step['transport']['type'] == 'walk' else 'driving')}
                     }})
            duration += step['duration']
    elif transport == 'train':
        title_to = 'Way to Peterhof: subway + suburban train'
        summary_to = 'Expenses: 95 RUR, travel time: 1h55'
        steps_to = [{'instruction': 'Go to Peterhof by train. We do not have details yet',
                     'start_time': utils.time_to_string(start_time),
                     'hint' : ''}]
    else:                
        title_to = 'Way to Peterhof: subway + bus'
        summary_to = 'Expenses: 95 RUR, travel time: 2h00'
        steps_to = [
            {'instruction': 'Leave the hotel and go to the subway station Sadovaya',
             'start_time': utils.time_to_string(start_time),
             'hint': 'on foot: 350 m',
             'details' :
             {
                'show_label': 'Show the map',
                'hide_label': 'Hide the map',
                'action' : 'map',
                'map': { 'points' : maps.get_route('59.9295,30.317', '59.9266,30.3175') }  
             },
            },
            {'instruction': 'Buy 2 tokens ("жетон") and enter in subway',
             'start_time': utils.time_to_string(utils.time_add_mins(start_time, 10)),
             'hint' : 'pay fare: 25 RUR'},
            {'instruction': 'You enter the subway at line 5 (purple). Take a train to Volkovskaya direction. ' +
                            'After 1 stop, get out of the train at Zvenigorodskaya station. Take a change to ' +
                            'Pushkinskaya station, line 1 (red). Take a train to Prospect Veteranov direction. ' +
                            'After 5 stops, exit to the city at Avtovo station.',
             'start_time': utils.time_to_string(utils.time_add_mins(start_time, 15)),
             'hint' : 'subway: 1 stop + change + 5 stops'},
            {'instruction': 'Leave the subway, cross the street through the underpass and find a bus stop',
             'start_time': utils.time_to_string(utils.time_add_mins(start_time, 40)),
             'hint' : 'on foot: 150 m',
             'details' :
             {
                'show_label': 'Show the map',
                'hide_label': 'Hide the map',
                'action': 'map',
                'map': { 'points' : maps.get_route('59.86758,30.261308', '59.868398,30.259806') }
             }
            },
            {'instruction': 'Take a minibus ("route-taxi"). Look for one of the following route numbers: К-424, ' +
                            'K-424a, К-300, К-224, К-401a, К-404 or any route-taxi where you see word "Фонтаны" ' + 
                            'on the window. Pay to driver, price may slightly vary. You should ask driver to stop in Petrodhof.',
             'start_time': utils.time_to_string(utils.time_add_mins(start_time, 45)),
             'hint' : 'pay fare: 70 RUR'},
            {'instruction': 'Leave route taxi on Pravlentskaya ulitsa and go to Lower Park entry',
             'start_time': utils.time_to_string(utils.time_add_mins(start_time, 105)),
             'hint' : 'on foot: 800 m',
             'details' :
             {
                'show_label': 'Show the map',
                'hide_label': 'Hide the map',
                'action' : 'map',
                'map': { 'points' : maps.get_route('59.883884,29.911548', '59.880511,29.906809') }
             }
            }]    
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
    
    context = { 'start_time' : utils.time_serialize(start_time) }
        
    return {'trips': [trip_to, trip_in], 'options': [option_bus, option_meteor, option_train], 'context': context}