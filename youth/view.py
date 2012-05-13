import os
import json
from google.appengine.ext.webapp import template

def to_html(data, template_name, response):
    path = os.path.join(os.path.dirname(__file__), 'templates', template_name + '.html')
    html = template.render(path, {'data': data})
    response.out.write(html)
    
def JsonHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj))    
    
def to_json(data, response):
    text = json.dumps(data, default = JsonHandler)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.out.write(text)