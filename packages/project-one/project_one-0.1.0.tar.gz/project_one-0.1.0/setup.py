# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['project_one']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'project-one',
    'version': '0.1.0',
    'description': 'Bamm_Files',
    'long_description': None,
    'author': 'Aghyad Farrouh',
    'author_email': 'external.Aghyad.Farrouh@bosch.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
