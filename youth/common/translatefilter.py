from django.utils.translation import ugettext as _
from google.appengine.ext import webapp
from django.utils import translation
# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

def translate(value):
    if value == 'LANGUAGE':
        return translation.get_language()
    elif value == 'LANGUAGE_FULL':
        return 'russian' if translation.get_language() == 'ru' else 'english'
    
    return _(value)

def html_dic():
    _("Home")
    _("About")
    _("First time in St. Petersburg")
    _("Get transport directions here")
    _("From")
    _("To")
    _("Print")
    _("Date and time")
    _("Get directions")
    _("try your hotel name or street address")
    _("try State Hermitage")
    _("Public transport transit in St. Petersburg")
    _("Get transport directions for tourist in St. Petersburg, Russia")
    
def other_dic():
    _('Bus')
    _('Share taxi')
    _('Trolleybus')
    _('Subway')
    _('Tram')
    _('Train') 

register.filter(translate)