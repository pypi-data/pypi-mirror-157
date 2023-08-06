# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['JS.py', 'JS.py.Build', 'js_fpy']

package_data = \
{'': ['*']}

install_requires = \
['alive-progress==2.4.1', 'pyparsing>=3.0.9,<4.0.0']

setup_kwargs = {
    'name': 'js-fpy',
    'version': '0.1.3',
    'description': 'A Python to JS transpiler',
    'long_description': '## Beta JS-fpy / JS-py',
    'author': 'Dragon',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
