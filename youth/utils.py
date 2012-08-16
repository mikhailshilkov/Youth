import datetime
import time
import re
import json

from google.appengine.ext import db
from django.utils import translation
from django.utils.translation import ugettext as _

def get_language():
    return translation.get_language()

def date_to_string(tm):
    return tm.strftime('%d %B %Y')

def date_serialize(tm):
    return tm.strftime('%Y-%m-%d')
 
def time_to_string(tm):
    return tm.strftime('%H:%M')

def time_serialize(tm):
    return tm.strftime('%H-%M')

def duration_to_string(duration):
    dur_int = int(round(duration))
    if dur_int > 120:
        return str(dur_int / 60) + ' ' + _('hours')+ ' ' + duration_to_string(dur_int % 60)
    elif duration > 60:
        return '1 ' +  _('hour') + ' ' + duration_to_string(dur_int % 60)
    elif duration <= 1:
        return '1 ' + _('min')
    else:
        return str(dur_int) + ' ' + _('mins')
    
def distance_to_string(meters):
    met_int = int(round(meters))
    if met_int >= 950:
        return '%.1f ' % (float(meters) / 1000) + _('km')
    elif meters > 300:
        return '%s ' % int(round(meters, -2)) + _('m')
    else:
        return '%s ' % int(round(meters, -1)) + _('m')

def price_to_string(rub):
    return '%s ' % int(rub) + _('RUB')

def stops_to_string(stops):
    if stops == 1:
        return '1 ' + _('stop') 
    elif stops <= 4:
        return str(stops) + ' ' + _('stops234')
    else:
        return str(stops) + ' ' + _('stops')

def subway_color(text, line):
    return '<span class="subwayline%s">' % line + text + '</span>'

def time_add_mins(tm, mins):
    fulldate = datetime.datetime(1,1,1,tm.hour,tm.minute,tm.second)
    fulldate = fulldate + datetime.timedelta(minutes = mins)
    return fulldate.time()

def time_get_delta_minutes(start, end):
    delta = datetime.datetime.combine(datetime.date.today(), end) - datetime.datetime.combine(datetime.date.today(), start)
    return delta.seconds / 60

def remove_html_tags(data):
    div = re.compile(r'<div.*?>')
    p = re.compile(r'<.*?>')
    return p.sub('', div.sub(', ', data))

def decode_unicode_references(data):
    return re.sub("&#(\d+)(;|(?=\s))", decode_unicode_references_callback, data)

def decode_unicode_references_callback(matches):
    sym_id = matches.group(1)
    try:
        return unichr(int(sym_id))
    except:
        return sym_id

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

def model_to_dict(model):
    output = {}

    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            ms = time.mktime(value.utctimetuple())
            ms += getattr(value, 'microseconds', 0) / 1000
            output[key] = int(ms)
        elif isinstance(value, db.GeoPt):
            output[key] = {'lat': value.lat, 'lon': value.lon}
        elif isinstance(value, db.Model):
            output[key] = model_to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))

    return output

def JsonHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj))    
    
def to_json(data):
    return json.dumps(data, default = JsonHandler)