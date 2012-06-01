from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from youth import controller

class MainHandler(webapp.RequestHandler):    
    
    def get(self):
        if self.request.path == '/':
            controller.do_home(self.request, self.response)
        elif self.request.path == '/itinerary':
            controller.do_itinerary(self.request, self.response)
        elif self.request.path == '/itinerary/trip':
            controller.do_itinerary_trip(self.request, self.response)
        elif self.request.path == '/itinerary/options':
            controller.do_itinerary_options(self.request, self.response)
        elif self.request.path == '/hotel':
            controller.do_hotel(self.request, self.response)
        elif self.request.path == '/attraction':
            controller.do_attraction(self.request, self.response)
        elif self.request.path == '/transit':
            controller.do_transit(self.request, self.response)
        elif self.request.path == '/train':
            controller.do_train(self.request, self.response)
        elif self.request.path == '/test':
            controller.do_test(self.request, self.response)
        else:
            controller.do_notfound(self.request, self.response)
            
    def post(self):
        if self.request.path == '/hotel':
            controller.post_hotel(self.request)
        elif self.request.path == '/attraction':
            controller.post_attraction(self.request)
            
    def delete(self):
        if self.request.path == '/hotel':
            controller.delete_hotel(self.request)
        elif self.request.path == '/attraction':
            controller.delete_attraction(self.request)

application = webapp.WSGIApplication([('.*', MainHandler)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
