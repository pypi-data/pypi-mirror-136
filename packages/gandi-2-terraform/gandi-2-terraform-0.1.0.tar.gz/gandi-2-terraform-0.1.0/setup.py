# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gandi_tf']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['gandi-2tf = gandi_tf.main:generate']}

setup_kwargs = {
    'name': 'gandi-2-terraform',
    'version': '0.1.0',
    'description': 'CLI to read Gandi.net live DNS records and generate corresponding TF files',
    'long_description': None,
    'author': 'Marc-Aurèle Brothier',
    'author_email': 'm@brothier.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
