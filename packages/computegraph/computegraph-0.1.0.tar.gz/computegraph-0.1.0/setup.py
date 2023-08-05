# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['computegraph']

package_data = \
{'': ['*']}

install_requires = \
['networkx>=2.6.2', 'numpy>=1.20.3']

setup_kwargs = {
    'name': 'computegraph',
    'version': '0.1.0',
    'description': 'computegraph is a tool for managing computational graphs using networkx',
    'long_description': '# computegraph\nTools for managing computation graphs based on dictionaries and networkx\n',
    'author': 'David Shipman',
    'author_email': 'dshipman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monash-emu/computegraph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<=3.11',
}


setup(**setup_kwargs)
