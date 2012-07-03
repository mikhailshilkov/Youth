from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from youth import controller

class MainHandler(webapp.RequestHandler):    
    
    def get(self):
        if self.request.path == '/':
            controller.do_home(self.request, self.response)
        elif self.request.path == '/directions':
            controller.do_directions(self.request, self.response)
        elif self.request.path == '/about':
            controller.do_about(self.request, self.response)
        elif self.request.path == '/place':
            controller.do_place(self.request, self.response)
        elif self.request.path == '/transit':
            controller.do_transit(self.request, self.response)
        elif self.request.path == '/routing':
            controller.do_routing(self.request, self.response)
        elif self.request.path == '/train':
            controller.do_train(self.request, self.response)
        elif self.request.path == '/test':
            controller.do_test(self.request, self.response)
        else:
            self.error(404)
            controller.do_notfound(self.request, self.response)
            
    def post(self):
        if self.request.path == '/hotel':
            controller.post_hotel(self.request)
        elif self.request.path == '/attraction':
            controller.post_attraction(self.request)
        elif self.request.path == '/param':
            controller.post_param(self.request, self.response)
            
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
