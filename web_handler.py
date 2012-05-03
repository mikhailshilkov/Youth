import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from youth import itinerary
from youth import view
from youth import stuff

class MainHandler(webapp.RequestHandler):    
    
    def get(self):  
        if self.request.get('test') == 'true':
            self.response.out.write(stuff.test())
            return
              
        # get request parameters
        try: 
            start_time = datetime.datetime.strptime(self.request.get('time', '10:00'), '%H:%M')
        except:
            start_time = datetime.time(hour=10, minute=0)
        view_mode = self.request.get('out', 'html')
        transport = self.request.get('transport', 'bus')

        # produce data        
        data = itinerary.get(start_time, transport)              
        
        # populate the requested view
        if view_mode == 'json':
            view.to_json(data, self.response)
        else:
            view.to_html(data, 'itinerary', self.response)     


application = webapp.WSGIApplication([('/', MainHandler)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
