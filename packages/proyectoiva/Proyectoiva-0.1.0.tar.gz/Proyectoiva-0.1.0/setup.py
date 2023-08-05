# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proyectoiva', 'proyectoiva.mensajes']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['saludo = Proyectoiva.main:main']}

setup_kwargs = {
    'name': 'proyectoiva',
    'version': '0.1.0',
    'description': 'Proyecto se trata de Arquitectura interior',
    'long_description': '## Proyecto bimestral \n',
    'author': 'Imanazco',
    'author_email': 'ivanna_ao97@outlook.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': '<https://github.com/JuanPerez/package_name>',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
