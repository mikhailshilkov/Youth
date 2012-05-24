import re
import urllib
from google.appengine.api import urlfetch
from lib.BeautifulSoup import BeautifulSoup
import datetime
import utils

class TrainTiming(object):
    def __init__(self, departure, arrival):
        self.departure = departure
        self.arrival = arrival
        
    def get_duration(self):
        return utils.time_get_delta_minutes(self.arrival, self.departure)

def fetch_trains(place_from, place_to, date):    
    params = {'fromName': place_from,
              'toName': place_to,
              'when': date.isoformat(),
              'search_type': 'suburban'}
    url = 'http://m.rasp.yandex.ru/search?' + urllib.urlencode(params)                    
    response = urlfetch.fetch(url)
    html = response.content
    soup = BeautifulSoup(html)
    list_node = soup.find("ul", { "class" : "b-holster b-search-result" })
    if list_node != None:
        regex = re.compile(r'<.*?>')
        b_nodes = list_node.findAll("b")
        result = []
        for b_node in b_nodes:
            data = regex.split(b_node.renderContents())
            time = [datetime.datetime.strptime(x, '%H:%M').time() for x in data]            
            result.append(TrainTiming(time[0], time[1]))
        return result