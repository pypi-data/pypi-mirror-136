# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['homestead',
 'homestead.core',
 'homestead.core.routes',
 'homestead.craft',
 'homestead.craft.commands',
 'homestead.craft.stubs',
 'homestead.craft.stubs.modules',
 'homestead.utils']

package_data = \
{'': ['*'], 'homestead.craft.stubs': ['views/*']}

install_requires = \
['cookiecutter>=1.0,<2.0',
 'fastapi>=0.70.1,<0.71.0',
 'questionary>=1.10.0,<2.0.0',
 'sqlmodel>=0.0.6,<0.0.7',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['craft = homestead.craft.main:app']}

setup_kwargs = {
    'name': 'homestead',
    'version': '0.0.3',
    'description': 'Python "framework" built on top of several popular frameworks and tools such as FastAPI.',
    'long_description': '',
    'author': 'Brandon Braner',
    'author_email': 'brandon.braner@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/HomesteadFramework/homestead',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
