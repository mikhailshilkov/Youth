from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from youth import controller

class MainHandler(webapp.RequestHandler):    
    
    def get(self):
        if self.request.path == '/':
            controller.do_home(self.request, self.response)
        elif self.request.path == '/itinerary':
            controller.do_itinerary(self.request, self.response)
        elif self.request.path == '/test':
            controller.do_test(self.request, self.response)
        else:
            controller.do_notfound(self.request, self.response)

application = webapp.WSGIApplication([('.*', MainHandler)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
