# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['touka', 'touka.callbacks', 'touka.utils']

package_data = \
{'': ['*']}

install_requires = \
['tinydb>=4.7.0,<5.0.0', 'typer>=0.4.2,<0.5.0']

entry_points = \
{'console_scripts': ['touka = touka.touka:main']}

setup_kwargs = {
    'name': 'touka.ssh',
    'version': '1.0.0',
    'description': 'touka.ssh is an ssh manager that allows you to manage all of your VPSs without keeping your password.',
    'long_description': '',
    'author': 'anil chauhan',
    'author_email': 'anilchauhanxda@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
