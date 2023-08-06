# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bite', 'bite.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bite-parser',
    'version': '0.1.1',
    'description': 'Asynchronous parser taking incremental bites out of your byte input stream.',
    'long_description': '.. image:: https://github.com/jgosmann/bite/actions/workflows/ci.yml/badge.svg\n  :target: https://github.com/jgosmann/bite/actions/workflows/ci.yml\n  :alt: CI and release pipeline\n.. image:: https://codecov.io/gh/jgosmann/bite/branch/main/graph/badge.svg?token=O4M05YWNQK\n  :target: https://codecov.io/gh/jgosmann/bite\n  :alt: Codecov coverage\n.. image:: https://img.shields.io/pypi/v/bite\n  :target: https://pypi.org/project/bite/\n  :alt: PyPI\n.. image:: https://img.shields.io/pypi/pyversions/bite\n  :target: https://pypi.org/project/bite/\n  :alt: PyPI - Python Version\n.. image:: https://img.shields.io/pypi/l/bite\n  :target: https://pypi.org/project/bite/\n  :alt: PyPI - License\n\nbite parser\n===========\n\nAsynchronous parser taking incremental bites out of your byte input stream.\n',
    'author': 'Jan Gosmann',
    'author_email': 'jan@hyper-world.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jgosmann/bite-parser/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<=3.10',
}


setup(**setup_kwargs)
