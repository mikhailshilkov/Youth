import os
from google.appengine.ext.webapp import template
from django.utils.translation import ugettext as _
from youth import utils

def to_html(data, template_name, request, response):
    path = os.path.join(os.path.dirname(__file__), 'templates', template_name + '.html')
    html = template.render(path, 
                           {'data': data, 
                            'active_page': template_name.replace('_ru', ''),
                            'switch_language_page': get_language_link(request.path_qs)
                            })
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
    
def get_language_link(path):
    language = utils.get_language()
    name = _('EnglishRu') if language == 'ru' else _('RussianEn')
    code = 'en' if language == 'ru' else 'ru'
    lang_path = path.replace('/'  + language, '/' + code)
    return '<a class="language" href="' + lang_path + '">' + name + '</a>'