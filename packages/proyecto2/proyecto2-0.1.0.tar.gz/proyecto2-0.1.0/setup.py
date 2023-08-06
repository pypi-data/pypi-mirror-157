# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proyecto2', 'proyecto2.mensajes']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['saludo = proyecto2.main:main']}

setup_kwargs = {
    'name': 'proyecto2',
    'version': '0.1.0',
    'description': '',
    'long_description': '## Sistema de monitoreo mediante sensores ##',
    'author': 'Isaac Bustos',
    'author_email': 'jibustos@utpl.edu.ec',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
