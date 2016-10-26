import jinja2
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

def datetimeformat(value, format='%b %d, %Y'):
    return value.strftime(format)

def render_str(template, **params):
    return jinja_env.get_template(template).render(params)

jinja_env.filters['datetimeformat'] = datetimeformat
