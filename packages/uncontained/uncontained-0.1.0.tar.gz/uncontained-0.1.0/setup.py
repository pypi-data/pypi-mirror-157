# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['uncontained']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'uncontained',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Nitzan Zada',
    'author_email': 'nitzan.zada@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
