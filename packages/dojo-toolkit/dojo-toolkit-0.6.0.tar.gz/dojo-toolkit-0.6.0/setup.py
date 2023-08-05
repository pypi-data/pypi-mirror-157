# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dojo_toolkit']

package_data = \
{'': ['*'], 'dojo_toolkit': ['assets/*', 'assets/sounds/*']}

install_requires = \
['clint>=0.5.1,<0.6.0', 'pyglet>=1.5.21,<2.0.0', 'watchdog>=2.1.6,<3.0.0']

extras_require = \
{':sys_platform == "linux"': ['pgi>=0.0.11,<0.0.12']}

entry_points = \
{'console_scripts': ['dojo = dojo_toolkit.main:main']}

setup_kwargs = {
    'name': 'dojo-toolkit',
    'version': '0.6.0',
    'description': 'Toolkit for Python Coding Dojos.',
    'long_description': None,
    'author': 'grupy-sanca',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
