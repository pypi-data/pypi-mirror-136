# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ovpn3']
install_requires = \
['backoff>=1.11.1,<2.0.0',
 'click-log>=0.3.2,<0.4.0',
 'click>=8.0.3,<9.0.0',
 'cryptography>=36.0.1,<37.0.0',
 'keyring>=23.4.0,<24.0.0',
 'xdg>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['ovpn3 = ovpn3:main']}

setup_kwargs = {
    'name': 'ovpn3',
    'version': '0.1.3',
    'description': 'OpenVPN3 CLI',
    'long_description': None,
    'author': 'Janusz Skonieczny',
    'author_email': 'pypi@wooyek.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
