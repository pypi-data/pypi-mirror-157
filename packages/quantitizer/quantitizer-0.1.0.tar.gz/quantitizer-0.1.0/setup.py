# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quantitizer', 'quantitizer.integration', 'quantitizer.integration.gensim']

package_data = \
{'': ['*']}

install_requires = \
['gensim>=4.2.0,<5.0.0', 'mega.py>=1.0.8,<2.0.0', 'numpy>=1.23.0,<2.0.0']

setup_kwargs = {
    'name': 'quantitizer',
    'version': '0.1.0',
    'description': 'This package allows to quantitize matrix to compress different ML models.',
    'long_description': None,
    'author': 'CapBlood',
    'author_email': 'stalker.anonim@mail.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
