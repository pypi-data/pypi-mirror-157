# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['touka', 'touka.callbacks', 'touka.database', 'touka.utils']

package_data = \
{'': ['*']}

install_requires = \
['prettytable>=3.3.0,<4.0.0', 'tinydb>=4.7.0,<5.0.0', 'typer>=0.4.2,<0.5.0']

entry_points = \
{'console_scripts': ['touka = touka.touka:main']}

setup_kwargs = {
    'name': 'touka.ssh',
    'version': '2.2.8',
    'description': 'touka.ssh is an ssh manager that allows you to manage all of your VPSs without keeping your password.',
    'long_description': '# touka.ssh\n> touka.ssh is an ssh manager that allows you to manage all of your VPSs without keeping your password.\n\n## Installing\n```\npip3 install -U touka.ssh\n```\n\n\n## help \n> touka --help\n```\nUsage: touka.ssh [OPTIONS] COMMAND [ARGS]...\n\n  Awesome ssh manager, especially made for anii ☂️\n\nOptions:\n  -v, --version  Show the application\'s version and exit.\n  --help                          Show this message and exit.\n\nCommands:\n  add      Add a new ssh connection with a description.\n  connect  connect to server via name\n  init     assign pub key to your IP machine\n  list     list of all saved servers.\n  purge    purge your stored servers.\n```\n## Init\nassign pub key to your IP machine\n```sh\ntouka init\n```\n\n## add\nAdd a new ssh connection with a description.\n```sh\ntouka add -a 192.168.0.9 -n meanii-ubuntu -d "meanii modlette\'s server digitalocean"\n```\n\n## list\nlist of all saved servers.\n\n```\nServers you have saved:\n\n+----+---------------------+----------------+------+---------------------------------------------------+--------+\n| ID |         Name        |    Address     | Port |                    Description                    | Status |\n+----+---------------------+----------------+------+---------------------------------------------------+--------+\n| 1  |   kube-anii-master  | 218.45.380.202 |  22  |     kube-anii-master  server of kubernaties       |   ✅   |\n| 2  | kube-anii-worker-02 | 308.50.380.204 |  22  |   kube-anii-worker-02  server of kubernaties      |   ✅   |\n| 3  | kube-anii-worker-01 | 308.50.254.203 |  22  |   kube-anii-worker-01  server of kubernaties      |   ✅   |\n| 4  |     jenkins         | 308.50.253.209 |  22  |      jenkins server - jenkins.meanii.dev          |   ✅   |\n+----+---------------------+----------------+------+---------------------------------------------------+--------+\n```\n\n## connect\nconnect to server via name\n```sh\ntouka connect -n meanii-ubuntu\n```\n\n---\n###  Copyright & License\n- Copyright (C)  2022 [meanii](https://github.om/meanii )\n- Licensed under the terms of the [GNU General Public License v3.0](https://github.com/meanii/touka.ssh/blob/main/LICENSE)',
    'author': 'anil chauhan',
    'author_email': 'anilchauhanxda@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
