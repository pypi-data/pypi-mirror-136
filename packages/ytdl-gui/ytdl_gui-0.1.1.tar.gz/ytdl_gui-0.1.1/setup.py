# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ytdl_gui']

package_data = \
{'': ['*']}

install_requires = \
['PyGObject>=3.42.0,<4.0.0', 'yt-dlp>=2022.1.21,<2023.0.0']

entry_points = \
{'console_scripts': ['ytdl-gui = ytdl_gui:main']}

setup_kwargs = {
    'name': 'ytdl-gui',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'sleepntsheep',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
