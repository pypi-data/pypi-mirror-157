# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sliceline']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.4,<2.0.0', 'scikit-learn>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'sliceline',
    'version': '0.1.0',
    'description': 'Sliceline is a Python library for fast slice finding for Machine Learning model debugging.',
    'long_description': None,
    'author': 'Antoine de Daran',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
