# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['personalissues']

package_data = \
{'': ['*']}

install_requires = \
['jira>=3.4.1,<4.0.0']

setup_kwargs = {
    'name': 'personalissues',
    'version': '0.1.2',
    'description': '',
    'long_description': '',
    'author': 'Jon Keatley',
    'author_email': 'jon@ebi.ac.uk',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
