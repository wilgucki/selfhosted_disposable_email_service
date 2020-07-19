import os

from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_template(template, data=None, headers=None, status_code=200):
    if data is None:
        data = {}

    if headers is None:
        headers = {}

    env = Environment(
        loader=FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))),
        autoescape=select_autoescape(['html'])
    )

    headers = {**{'Content-Type': 'text/html'}, **headers}

    return {
        'statusCode': status_code,
        'headers': headers,
        'body': env.get_template(template).render(data)
    }
