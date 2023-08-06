# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ramose']
install_requires = \
['Click==7.0',
 'Flask==1.1.1',
 'Jinja2==2.11.3',
 'Markdown==3.1.1',
 'MarkupSafe==1.1.1',
 'Werkzeug==0.16.0',
 'certifi==2019.11.28',
 'chardet==3.0.4',
 'idna==2.8',
 'isodate==0.6.1',
 'itsdangerous==1.1.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'rdflib==6.1.1',
 'requests>=2.22.0,<3.0.0',
 'six==1.13.0',
 'urllib3==1.26.5']

setup_kwargs = {
    'name': 'ramose',
    'version': '1.0.6',
    'description': 'Restful API Manager Over SPARQL Endpoints (RAMOSE) is an application that allows agile development and publication of documented RESTful APIs for querying SPARQL endpoints, according to a particular specification document.',
    'long_description': None,
    'author': 'essepuntato',
    'author_email': 'essepuntato@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/opencitations/ramose/',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
