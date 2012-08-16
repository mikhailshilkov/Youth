import re
import urllib
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from lib.BeautifulSoup import BeautifulSoup
import datetime
import utils

class TrainTiming(object):
    def __init__(self, departure, arrival):
        self.departure = departure
        self.arrival = arrival
        
    def get_duration(self):
        return utils.time_get_delta_minutes(self.departure, self.arrival)

def fetch_trains(place_from, place_to, date):  
    key = 'trains_' + place_from + '_' + place_to + '_' + str(date)
    data = memcache.get(key) #@UndefinedVariable
    if data != None:
        return data
      
    params = {'fromName': unicode(place_from).encode('utf-8'),
              'toName': unicode(place_to).encode('utf-8'),
              'when': utils.date_serialize(date),
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
        last_hour = 0
        for b_node in b_nodes:
            data = regex.split(b_node.renderContents())
            try:
                time = [datetime.datetime.strptime(x, '%H:%M').time() for x in data]
                if last_hour > time[0].hour: # we are on next day already
                    break
                last_hour = time[0].hour
                result.append(TrainTiming(time[0], time[1]))
            except:
                pass
        memcache.add(key, result, 60*60)  #@UndefinedVariable
        return result