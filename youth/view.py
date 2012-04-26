import os
import json
from google.appengine.ext.webapp import template

def to_html(data, template_name, response):
    path = os.path.join(os.path.dirname(__file__), 'templates', template_name + '.html')
    html = template.render(path, {'data': data})
    response.out.write(html)       
    
def to_json(data, response):
    text = json.dumps(data)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.out.write(text)