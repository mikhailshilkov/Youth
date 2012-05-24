from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from youth import controller

class MainHandler(webapp.RequestHandler):    
    
    def get(self):
        if self.request.path == '/':
            controller.do_home(self.request, self.response)
        elif self.request.path == '/itinerary':
            controller.do_itinerary(self.request, self.response)
        elif self.request.path == '/itinerary_js':
            controller.do_itinerary(self.request, self.response, 'itinerary_js')
        elif self.request.path == '/hotel':
            controller.do_hotel(self.request, self.response)
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
            
    def delete(self):
        if self.request.path == '/hotel':
            controller.delete_hotel(self.request)

application = webapp.WSGIApplication([('.*', MainHandler)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
