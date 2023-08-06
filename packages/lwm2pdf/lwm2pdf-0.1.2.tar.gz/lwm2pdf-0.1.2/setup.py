# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lwm2pdf']

package_data = \
{'': ['*'], 'lwm2pdf': ['themes/*', 'themes/source/*']}

install_requires = \
['asciidoc>=10.2.0,<11.0.0', 'markdown2>=2.4.3,<3.0.0', 'weasyprint==52.5']

entry_points = \
{'console_scripts': ['lwm2pdf = lwm2pdf.main:lwm2pdf']}

setup_kwargs = {
    'name': 'lwm2pdf',
    'version': '0.1.2',
    'description': 'Takes a variety of lighweight markup files and returns PDFs styled with provided css (via WeasyPrint)',
    'long_description': None,
    'author': 'Danny Elfanbaum',
    'author_email': 'drelfanbaum@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
