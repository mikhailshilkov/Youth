import os
import webapp2
import urllib2
import random
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import translation
from youth import controller
from youth import rater

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
settings._target = None

class MainHandler(webapp2.RequestHandler): 
    def __init__(self, request, response):
        self.initialize(request, response)
        translation.activate('en')
                 
    def get(self):
        path = urllib2.unquote(self.request.path)
        
        if path == '/service/hotelrating':
            r = random.random()
            if r < 0.2:
                controller.do_calculate_hotel_rating(self.request, self.response);
            elif r > 0.98:
                rater.get_all()
        elif path == '/service/cleanup':
            controller.do_cleanup(self.request, self.response);
        else:
            self.error(404)
            controller.do_notfound(self.request, self.response)       

application = webapp2.WSGIApplication([('.*', MainHandler)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
