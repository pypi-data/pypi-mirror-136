# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wgeasywall',
 'wgeasywall.cmd',
 'wgeasywall.cmd.config',
 'wgeasywall.cmd.network',
 'wgeasywall.utils',
 'wgeasywall.utils.IPtable',
 'wgeasywall.utils.general',
 'wgeasywall.utils.graphml',
 'wgeasywall.utils.mongo',
 'wgeasywall.utils.mongo.core',
 'wgeasywall.utils.mongo.table',
 'wgeasywall.utils.nacl',
 'wgeasywall.utils.parse',
 'wgeasywall.utils.ruleAsCode',
 'wgeasywall.utils.wireguard']

package_data = \
{'': ['*'], 'wgeasywall': ['RaaCManifest/*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'coolname>=1.1.0,<2.0.0',
 'deepdiff>=5.5.0,<6.0.0',
 'donna25519>=0.1.1,<0.2.0',
 'ipaddr>=2.2.0,<3.0.0',
 'netaddr>=0.8.0,<0.9.0',
 'networkx>=2.6.3,<3.0.0',
 'prettyprint>=0.1.5,<0.2.0',
 'pydantic>=1.8.2,<2.0.0',
 'pymongo>=3.12.0,<4.0.0',
 'python-hosts>=1.0.1,<2.0.0',
 'pyyed>=1.4.3,<2.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['wgeasywall = wgeasywall.main:app']}

setup_kwargs = {
    'name': 'wgeasywall',
    'version': '0.1.1',
    'description': 'A CLI tool for managing WireGuard networks and IPTables by using GraphML',
    'long_description': '\n## What is WGEasywall\n[WGEasywall](https://github.com/araminian/wgeasywall) is a CLI to manage Wireguard networks and IPTables rules using GraphML\n\n\n## How to Install and Configure WGEasywall\n\nWGEasywall needs python version 3.8 or above. It can be installed using following command:\n\n```bash\npip install wgeasywall\n```\n\nWGEasywall needs MongoDB database to start working. We should tell it how to access the database using following command:\n\n```bash\nwgeasywall config generate database --mongodb-address [MongoDB Address] --mongodb-user [USER] --mongodb-password [PASSWORD]\n```\n\n> **_NOTE:_**  WGEasywall access database using default port 27017 and it can not be changed\n\n\nWGEasywall IPTables rule generator needs `Rule as a Code` `Actions and Function` manifest file. These manifest files should be imported to the WGEasywall. These manifest files are located in `RaaCManifest` folder.\nWe can import these files using following commands:\n\n```bash\n# import general function\nwgeasywall RaaC import-function --function-file General.yaml\n\n# import DROP action\nwgeasywall RaaC import-action --action-file DROP.yaml\n\n# import ACCEPT action\nwgeasywall RaaC import-action --action-file ACCEPT.yaml\n\n# import LOG action\nwgeasywall RaaC import-action --action-file LOG.yaml\n```\n\n> **_NOTE:_**  These manifest can be changed but they should be compatible with WGEasywall \n\nNow wgeasywall is ready for managing WireGuard networks and IPTables rules.\n',
    'author': 'Armin Aminian',
    'author_email': 'rmin.aminian@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
