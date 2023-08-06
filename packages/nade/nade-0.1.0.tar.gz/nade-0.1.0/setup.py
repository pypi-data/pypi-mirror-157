# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nade', 'nade.data']

package_data = \
{'': ['*'], 'nade.data': ['socialmedia_en/*']}

install_requires = \
['fasttext>=0.9.0,<0.10.0',
 'lightgbm>=3.2,<4.0',
 'numpy>=1.19,<2.0',
 'pyarrow>=6.0.1,<7.0.0']

setup_kwargs = {
    'name': 'nade',
    'version': '0.1.0',
    'description': 'Natural affect detection allows to infer basic emotions from social media messages',
    'long_description': None,
    'author': 'Christian Hotz-Behofsits',
    'author_email': 'chris.hotz.behofsits@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
