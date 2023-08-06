# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybuoy', 'pybuoy.api', 'pybuoy.mixins']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'pybuoy',
    'version': '0.1.0',
    'description': 'Python wrapper for NDBC data.',
    'long_description': '# pybuoy\n\n`pybuoy` is a server-side Python package that serves as a convenience wrapper for clairBuoyant to faciliate rapid discovery of new data for surf forecasting models.\n',
    'author': 'Kyle J. Burda',
    'author_email': 'kylejbdev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
