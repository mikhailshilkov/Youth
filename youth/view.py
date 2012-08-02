import os
from google.appengine.ext.webapp import template
from youth import utils

def to_html(data, template_name, request, response):
    path = os.path.join(os.path.dirname(__file__), 'templates', template_name + '.html')
    html = template.render(path, {'data': data, 'active_page': template_name})
    response.write(html)
    
def to_jinja_html(data, template_name, request, response, jinja2):
    html = jinja2.render_template(template_name + '.html', data = data, request = request)
    response.write(html)
    
def to_json(data, response):
    text = utils.to_json(data)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.write(text)
    
def empty(response):
    response.write('None')