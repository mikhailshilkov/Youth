import json
import math
import param
from lib import geo

def get_route(start_location, end_location):
    subway_dict = json.loads(param.get('subway'))
    graph = StationGraph()
    graph.stations = [Station(x['name'], x['lat'], x['lng'], x['line']) for x in subway_dict['stations']]
    graph.links = [StationLink(x['from_station'], x['to_station'], x['duration']) for x in subway_dict['links']]
    return get_route_ongraph(graph, start_location, end_location)

def get_route_ongraph(graph, start_location, end_location):
    entrances = [x for x in graph.stations if x.name != 'Spasskaya']
    
    near_start = find_near(entrances, start_location.lat, start_location.lng)
    start = Station('Start', start_location.lat, start_location.lng, None)
    graph.stations.append(start)
    for station in near_start:
        graph.links.append(StationLink('Start', station.name, station.estimate_walk_time_to(start_location.lat, start_location.lng)))

    near_end = find_near(entrances, end_location.lat, end_location.lng)
    end = Station('End', end_location.lat, end_location.lng, None)
    graph.stations.append(end)
    for station in near_end:
        graph.links.append(StationLink(station.name, 'End', station.estimate_walk_time_to(end_location.lat, end_location.lng)))
        
    path = AStar(graph, start, end)
    return path

def find_near(stations, lat, lng):
    less_20_min = [x for x in stations if x.estimate_walk_time_to(lat, lng) < 1200]
    if len(less_20_min) > 0:
        return less_20_min
    else:
        return [find_nearest(stations, lat, lng)]

def find_nearest(stations, lat, lng):
    return min(stations, key=lambda x: x.estimate_subway_time_to(lat, lng))

def AStar(graph, start, goal):
    closedset = []    # The set of nodes already evaluated.
    openset = [start]    # The set of tentative nodes to be evaluated, initially containing the start node
    came_from = {}#the empty map    # The map of navigated nodes.
    g_score = {}
    f_score = {}
 
    g_score[start] = 0    # Cost from start along best known path.
    # Estimated total cost from start to goal through y.
    f_score[start] = g_score[start] + heuristic_cost_estimate(start, goal)
 
    while len(openset) > 0:
        current = min(openset, key=lambda x: f_score[x]) #the node in openset having the lowest f_score[] value
        if current == goal:
            return reconstruct_path(came_from, goal)
 
        openset.remove(current)
        closedset.append(current)
        neighbor_nodes = graph.get_neighbor_nodes(current)
        for neighbor in neighbor_nodes:    
            if neighbor in closedset:
                continue
            distance = graph.dist_between(current, neighbor)
            tentative_g_score = g_score[current] + distance
 
            if neighbor not in openset or tentative_g_score < g_score[neighbor]: 
                openset.append(neighbor)
                came_from[neighbor] = { 'node': current, 'distance': distance } 
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic_cost_estimate(neighbor, goal)
 
    return None #failure
 
def reconstruct_path(came_from, current_node, distance = 0):    
    if current_node in came_from:
        next_node = came_from[current_node]
        result = reconstruct_path(came_from, next_node['node'], next_node['distance'])
    else:
        result = []
    if current_node.name <> 'Start' and current_node.name <> 'End':
        result.append({ 'node': current_node, 'distance': distance })
    return result
    
def heuristic_cost_estimate(start, goal):
    return goal.estimate_subway_time_to(start.lat, start.lng)

class StationGraph(object):
    def __init__(self):
        self.stations = []
        self.links = []
        
    def by_name(self, name):
        return [x for x in self.stations if x.name == name][0] 
        
    def get_neighbor_nodes(self, node):
        links = [self.by_name(x.to_station) for x in self.links if x.from_station == node.name]
        return links

    def dist_between(self, start, end):
        return [x.duration for x in self.links 
                if x.from_station == start.name and x.to_station == end.name][0]
    
    def jsonable(self):
        return self.__dict__

                
class Station(object):
    def __init__(self, name, lat, lng, line):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.line = line
        
    def estimate_subway_time_to(self, lat, lng):
        return int(math.sqrt((self.lat - lat)**2 + (self.lng - lng)**2) * 8000) # 8000 is an apprx const, doesn't mean anything
    
    def estimate_walk_time_to(self, lat, lng): 
        return int(geo.haversine(self.lng, self.lat, lng, lat) * 60 / 80) # result in seconds
    
    def jsonable(self):
        return self.__dict__
    
class StationLink(object):
    def __init__(self, from_station, to_station, duration):
        self.from_station = from_station
        self.to_station = to_station
        self.duration = duration
        
    def jsonable(self):
        return self.__dict__