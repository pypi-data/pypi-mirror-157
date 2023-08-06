# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['docufix']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['docufix = docufix.__main__:main']}

setup_kwargs = {
    'name': 'docufix',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Nyakku Shigure',
    'author_email': 'sigure.qaq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
