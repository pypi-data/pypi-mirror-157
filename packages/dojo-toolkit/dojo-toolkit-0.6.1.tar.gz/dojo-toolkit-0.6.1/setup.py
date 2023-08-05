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
    'version': '0.6.1',
    'description': 'Toolkit for Python Coding Dojos.',
    'long_description': "Dojo Toolkit\n============\n\n.. image:: https://github.com/grupy-sanca/dojo-toolkit/actions/workflows/test_push.yaml/badge.svg?branch=main\n  :target: https://github.com/grupy-sanca/dojo-toolkit/actions/workflows/test_push.yaml?query=branch%3Amain\n\n.. image:: https://coveralls.io/repos/github/grupy-sanca/dojo-toolkit/badge.svg?branch=main\n  :target: https://coveralls.io/github/grupy-sanca/dojo-toolkit?branch=main\n\n\nToolkit for python coding dojos.\n\nSource: https://github.com/grupy-sanca/dojo-toolkit\n\n\nFeatures\n--------\n- Timer to determine the pilot's turn\n- Display notifications on pilot's time up, tests passed and failed\n- Dojo Semaphor through OS notifications\n- Run tests after each save\n\n\nHow to use\n----------\n\nInstallation:\n::\n\n  $ pip install dojo-toolkit\n\n\nRunning:\n::\n\n  $ dojo /path/to/code/directory/\n\n\nFor detailed information about running from source: `CONTRIBUING.rst <https://github.com/grupy-sanca/dojo-toolkit/blob/main/CONTRIBUTING.rst>`_\nTo see the options available use:\n::\n\n  $ dojo --help\n\n\nContributing\n------------\n\nCheck the `CONTRIBUING.rst <https://github.com/grupy-sanca/dojo-toolkit/blob/main/CONTRIBUTING.rst>`_ file to discover how you can help the development of dojo-toolkit.\n\n\nDependencies\n------------\n- Python 3\n- `Libnotify <https://developer.gnome.org/libnotify>`_\n\n\nRoadmap\n-------\n\n**0.5**\n\nTDB\n\n\nChangelog\n---------\n\n**0.4**\n\n- Tests + CI\n- Sound notifications\n- Minor bug fixes\n- Minor improvements\n\n**0.3**\n\n- Major refactor\n- Uses bumpversion\n\n**0.2**\n\n- Project improvements\n- Release to PyPI\n\n**0.1**\n\n- Timer for managing rounds\n- Watch code folder and run doctests on changes\n- Show notifications using Libnotify\n",
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
