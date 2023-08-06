# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyanbot', 'cyanbot.context', 'cyanbot.instance', 'cyanbot.plugin']

package_data = \
{'': ['*']}

install_requires = \
['concap>=0.2.1,<0.3.0', 'cookiecutter>=1.7,<2.0', 'cyansdk>=0.2.0,<0.3.0']

entry_points = \
{'console_scripts': ['cyanbot = cyanbot.__main__:main']}

setup_kwargs = {
    'name': 'cyanbot',
    'version': '0.1.1',
    'description': 'An integrated manager for Cyan Python SDK for QQ Bot.',
    'long_description': '# cyan-bot\n\n基于 Cyan SDK 的 QQ 机器人集成式管理工具',
    'author': 'worldmozara',
    'author_email': 'worldmozara@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.huajitech.net/huajitech/cyan-bot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
