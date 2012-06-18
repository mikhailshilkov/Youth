import json
import math
from youth import param

def get_route(from_addr, to_addr):
    subway_dict = json.loads(param.get('subway'))
    graph = StationGraph()
    graph.stations = [Station(x['name'], x['lat'], x['lng'], x['line']) for x in subway_dict['stations']]
    graph.links = [StationLink(x['from_station'], x['to_station'], x['duration']) for x in subway_dict['links']]

    [start_lat, start_lng] = [float(x) for x in from_addr.split(',')]
    [end_lat, end_lng] = [float(x) for x in to_addr.split(',')]

    start = find_nearest(graph.stations, start_lat, start_lng)
    end = find_nearest(graph.stations, end_lat, end_lng)
    path = AStar(graph, start, end)
    return path

def find_nearest(stations, lat, lng):
    return min(stations, key=lambda x: x.estimate_distance_to(lat, lng))

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
    result.append({ 'node': current_node, 'distance': distance })
    return result
    
def heuristic_cost_estimate(start, goal):
    return goal.estimate_distance_to(start.lat, start.lng)

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
        
    def estimate_distance_to(self, lat, lng):
        return int(math.sqrt((self.lat - lat)**2 + (self.lng - lng)**2) * 8000) # 8000 is an apprx const, doesn't mean anything 
    
    def jsonable(self):
        return self.__dict__
    
class StationLink(object):
    def __init__(self, from_station, to_station, duration):
        self.from_station = from_station
        self.to_station = to_station
        self.duration = duration
        
    def jsonable(self):
        return self.__dict__