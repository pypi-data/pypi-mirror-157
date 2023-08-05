# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['time_tracker_tui', 'time_tracker_tui.views', 'time_tracker_tui.widgets']

package_data = \
{'': ['*']}

install_requires = \
['platformdirs>=2.5.2,<3.0.0', 'textual>=0.1.18,<0.2.0']

entry_points = \
{'console_scripts': ['time-tracker = time_tracker_tui.__main__:main']}

setup_kwargs = {
    'name': 'time-tracker-tui',
    'version': '0.3.3',
    'description': 'Simple tui time tracker',
    'long_description': None,
    'author': 'Mark Bragin',
    'author_email': 'm4rk.brag1n@gmail.com',
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
