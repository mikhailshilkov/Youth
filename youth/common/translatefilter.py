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
    _("Hotels")
    _("Check prices")
    _("Total travel time to important Points of Interest")
    _("Hotel rating info")
    _("Point of Interest")
    _("with rooms from")
    _("Route to")
    _("Route from")
    _("Map")
    _("All")
    _("5-star")
    _("4-star")
    _("3-star")
    _("2-star")
    _("1-star")
    _("Filter by stars")
    _("Contact")
    _("Special offers")
    _("Copyright")
    _("2% discount on Booking.com")
    _("St. Petersburg, Russia")
    
def other_dic():
    _('Bus')
    _('Share taxi')
    _('Trolleybus')
    _('Subway')
    _('Tram')
    _('Train') 
    _('Hotel')
    _('Motel')
    _('Inn')
    _('Bed & Breakfast')
    _('Vacation Rental')
    _('Hostel')
    _('Retreat')
    _('Resort')
    _('Other')
    _('Apartment')

register.filter(translate)