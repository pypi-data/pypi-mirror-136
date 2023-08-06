# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vk_photos_uploader']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'tqdm>=4.62.3,<5.0.0', 'vk-api>=11.9.6,<12.0.0']

entry_points = \
{'console_scripts': ['vk_photos_uploader = '
                     'vk_photos_uploader.photos_uploader:upload_photos_to_album']}

setup_kwargs = {
    'name': 'vk-photos-uploader',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Gevorg Vardanyan',
    'author_email': 'gevorg_vardanyan@protonmail.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
