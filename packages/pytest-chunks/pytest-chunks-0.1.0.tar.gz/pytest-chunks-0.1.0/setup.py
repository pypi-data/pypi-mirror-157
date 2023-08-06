# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_chunks', 'pytest_chunks.tests']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=6.0.0']

entry_points = \
{'pytest11': ['pytest_chunks = pytest_chunks']}

setup_kwargs = {
    'name': 'pytest-chunks',
    'version': '0.1.0',
    'description': 'Run only a chunk of your test suite',
    'long_description': None,
    'author': 'Mehdi Abaakouk',
    'author_email': 'sileht@sileht.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
