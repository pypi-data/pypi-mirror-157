# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cic_helper']

package_data = \
{'': ['*'], 'cic_helper': ['kitabu/*']}

install_requires = \
['chainlib-eth>=0.1.0,<0.2.0', 'click>=8.1.2,<9.0.0']

entry_points = \
{'console_scripts': ['cic-helper = cic_helper.cli:cli']}

setup_kwargs = {
    'name': 'cic-helper',
    'version': '0.2.4',
    'description': '',
    'long_description': None,
    'author': 'William Luke',
    'author_email': 'williamluke4@gmail.com',
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
