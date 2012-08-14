import os
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext import webapp
from youth import controller

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
settings._target = None

from django.utils import translation
import webapp2
import urllib2

AVAILABLE_LOCALES = ['en', 'ru']

class MainHandler(webapp2.RequestHandler):      
    def __init__(self, request, response):
        self.initialize(request, response)

        language = None
        if self.request.path.startswith('/en'):
            language = 'en'
        elif self.request.path.startswith('/ru'):
            language = 'ru'
        if language != None:
            translation.activate(language)
        else:
            # first, try and set locale from cookie
            language = request.cookies.get('locale')
            if not language in AVAILABLE_LOCALES:
                # if that failed, try and set locale from accept language header
                header = request.headers.get('Accept-Language', '')  # e.g. en-gb,en;q=0.8,es-es;q=0.5,eu;q=0.3
                locales = [locale.split(';')[0] for locale in header.split(',')]
                for locale in locales:
                    if locale in AVAILABLE_LOCALES:
                        language = locale
                        break
                
            if language == None:
                # if still no locale set, use the first available one
                language = AVAILABLE_LOCALES[0]
            self.redirect('/' + language + self.request.path_qs)

    def get(self):
        language = None
        if self.request.path.startswith('/en'):
            language = 'en'
        elif self.request.path.startswith('/ru'):
            language = 'ru'
        if language != None:
            translation.activate(language)
        path = urllib2.unquote(self.request.path.replace('/en','').replace('/ru',''))
        
        if path == '' or path == '/':
            controller.do_home(self.request, self.response)
        elif path == '/directions':
            controller.do_directions(self.request, self.response)
        elif path == '/about':
            controller.do_about(self.request, self.response)
        elif path == '/place':
            controller.do_place(self.request, self.response)
        elif path == '/transit':
            controller.do_transit(self.request, self.response)
        elif path == '/routing':
            controller.do_routing(self.request, self.response)
        elif path == '/train':
            controller.do_train(self.request, self.response)
        elif path == '/hotels':
            controller.do_hotels(self.request, self.response)
        elif path.startswith('/hotel/'):
            controller.do_hotel(self.request, self.response, path.replace('/hotel/', ''))
        elif path == '/test':
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

webapp.template.register_template_library('youth.common.translatefilter')
application = webapp2.WSGIApplication([('.*', MainHandler)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
