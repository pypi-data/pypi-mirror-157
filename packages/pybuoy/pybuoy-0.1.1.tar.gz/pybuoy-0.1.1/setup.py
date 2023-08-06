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
    'version': '0.1.1',
    'description': 'Python wrapper for NDBC data.',
    'long_description': '![PyPI - Version](https://img.shields.io/pypi/v/pybuoy?color=blue)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pybuoy)\n![PyPI - Monthly Downloads](https://img.shields.io/pypi/dm/pybuoy)\n\n# pybuoy\n\n`pybuoy` is a server-side Python package that serves as a convenience wrapper for clairBuoyant to faciliate rapid discovery of new data for surf forecasting models with only a single dependency!\n\n## Installation\n\n`pybuoy` is supported on Python 3.10+. The [recommended way to install](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments) `pybuoy` is with `pip` and `virtualenv`.\n\n### Alternative\n\nI like to use [poetry](https://python-poetry.org) and it can be as easy as `poetry add pybuoy` within your project.\n\nFor more information on what and how to work with poetry, [click here](https://realpython.com/dependency-management-python-poetry).\n\n## Quickstart\n\n```python\n# Demo in python/ipython shell\n# Don\'t forget to install pybuoy first\n\n>>> from pybuoy import Buoy\n\n>>> buoy = Buoy(station_id="44065")\n\n>>> buoy\n<pybuoy.buoy.Buoy object at 0x10481fc10>\n```\n\n## Examples\n\n- [Get all active stations](./docs/examples/get_activestations.py).\n\n- [Get realtime meteorological data](./docs/examples/get_activestations.py) for buoy by station_id.\n',
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
