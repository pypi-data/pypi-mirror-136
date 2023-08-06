# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['texas', 'texas.holdem', 'texas.sub']

package_data = \
{'': ['*'], 'texas': ['data/*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'nbformat>=5.1.3,<6.0.0',
 'pandas>=1.4.0,<2.0.0',
 'plotly>=5.5.0,<6.0.0',
 'rich>=11.0.0,<12.0.0',
 'seaborn>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'texas',
    'version': '0.0.0',
    'description': '',
    'long_description': None,
    'author': 'agarichan',
    'author_email': 'ag4r1chan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
