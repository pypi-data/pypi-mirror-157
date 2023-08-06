# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_horserace']

package_data = \
{'': ['*'], 'nonebot_plugin_horserace': ['events/*']}

install_requires = \
['nonebot-adapter-onebot>=2.1.1,<3.0.0',
 'nonebot-plugin-imageutils>=0.1.6,<0.2.0',
 'nonebot2>=2.0.0-beta.4,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-horserace',
    'version': '2.2',
    'description': 'horserace',
    'long_description': None,
    'author': 'shinian',
    'author_email': '2581846402@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
