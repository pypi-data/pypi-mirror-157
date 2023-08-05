# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kims_great_shiny_package']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'kims-great-shiny-package',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Kim Hepperle',
    'author_email': 'kim-leonie.hepperle@telekom.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
