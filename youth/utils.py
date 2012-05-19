import datetime
import time
import re
import json

from google.appengine.ext import db
 
def time_to_string(tm):
    return tm.strftime('%I:%M %p')

def duration_to_string(duration):
    if duration > 120:
        return str(duration / 60) + ' hours ' + duration_to_string(duration % 60)
    elif duration > 60:
        return '1 hour ' + duration_to_string(duration % 60)
    elif duration == 1:
        return '1 min'
    else:
        return str(duration) + ' mins'

def time_serialize(tm):
    return tm.strftime('%H:%M')

def time_add_mins(tm, mins):
    fulldate = datetime.datetime(1,1,1,tm.hour,tm.minute,tm.second)
    fulldate = fulldate + datetime.timedelta(minutes = mins)
    return fulldate.time()

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

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