#from google.appengine.api import urlfetch
#import json
#import urllib

#        saddr = urllib.quote("St. Petersburg Shavrova 13")
#        daddr = urllib.quote("St. Petersburg Sadovaya 32")
#        saddr = urllib.quote("Stokholm")
#        daddr = urllib.quote("Uppsals")
#        url = "http://maps.google.com/?saddr=" + saddr + "&daddr=" + daddr + "&dirflg=r&output=json"
#        result = urlfetch.fetch(url)
#        if result.status_code == 200:
#            try:
#                routeJson = result.content.replace('while(1);','')
#                route = json.loads(routeJson)
#                self.response.out.write(route)
#            except:
#                self.response.out.write(routeJson)
#        else:
#            html = template.render('templates/test.html', {})
#            self.response.out.write(html)   