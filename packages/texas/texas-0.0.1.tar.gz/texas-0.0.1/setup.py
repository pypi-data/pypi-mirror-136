# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['texas', 'texas.holdem', 'texas.sub']

package_data = \
{'': ['*'], 'texas': ['data/*']}

setup_kwargs = {
    'name': 'texas',
    'version': '0.0.1',
    'description': 'botを作るためのフレームワークです',
    'long_description': '# TexasHoldem\n\n<a href="https://github.com/agarichan/texas/actions/workflows/test.yaml" target="_blank">\n  <img src="https://github.com/agarichan/texas/actions/workflows/test.yaml/badge.svg?branch=main" alt="Test">\n</a>\n<a href="https://codecov.io/gh/agarichan/texas" target="_blank">\n  <img src="https://img.shields.io/codecov/c/github/agarichan/texas?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/texas" target="_blank">\n  <img src="https://img.shields.io/pypi/v/texas?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/texas" target="_blank">\n  <img src="https://img.shields.io/pypi/pyversions/texas.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n\n## test\n\n時間のかかる test も全て行う場合は`--runslow`オプションをつける\n\n```\npytest --runslow\n```\n',
    'author': 'agarichan',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/agarichan/exmachina',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
