# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyhof']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyhof',
    'version': '0.1.4',
    'description': 'Python High Order Functions library',
    'long_description': "# pyhof\npyhof extends python's functools module.\n\nOriginally [borrowed from here](https://github.com/abarnert/more-functools)\n",
    'author': 'PyGamer0',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PyGamer0/functools_plus',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>3.7',
}


setup(**setup_kwargs)
