# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['h_devops']

package_data = \
{'': ['*']}

install_requires = \
['psutil>=5.9.1,<6.0.0', 'tabulate>=0.8.10,<0.9.0', 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['h-devops = h_devops.main:app']}

setup_kwargs = {
    'name': 'h-devops',
    'version': '0.3.2',
    'description': 'Tools to assist devops using CLI',
    'long_description': "# h_devops v0.3.2\n\n_Python support package from 3.6 and up_\n\n---\n\n# How to install\n\nPlease run this command on your terminal window 🎉️ \n\n```shell\n$ pip install h-devops\n```\n\nor\n\n```shell\n$ pip3 install h-devops\n```\n\n---\n\n# How to use\n\nWelcome to my world 😄 \n\nNow you can use the package with alias **h-devops**\n\n```shell\n$ h-devops --help\n```\n\n> Oh !! You will most likely encounter problems during use. I'm so sorry about this. :'(\n>\n> If you don't mind, you can **feedback** the error to me by email: **levuthanhtung11@gmail.com**\n>\n> I am so happy about that ❤️ \n>\n> Author: Võ Hoàng\n",
    'author': 'Vo Viet Hoang',
    'author_email': 'levuthanhtung11@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
