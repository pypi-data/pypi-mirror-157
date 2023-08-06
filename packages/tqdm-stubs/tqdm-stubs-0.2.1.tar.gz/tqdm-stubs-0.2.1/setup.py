# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tqdm-stubs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tqdm-stubs',
    'version': '0.2.1',
    'description': 'Stub type files for tqdm',
    'long_description': "==========================\ntqdm-stubs\n==========================\n\n.. image:: https://img.shields.io/pypi/v/tqdm_stubs\n   :alt: PyPI Package\n   :target: https://pypi.org/project/tqdm_stubs\n.. image:: https://img.shields.io/pypi/dm/tqdm_stubs\n   :alt: PyPI Downloads\n   :target: https://pypi.org/project/tqdm_stubs\n.. image:: https://img.shields.io/pypi/l/tqdm_stubs\n   :alt: License\n   :target: https://github.com/charmoniumQ/tqdm-stubs/blob/main/LICENSE\n.. image:: https://img.shields.io/pypi/pyversions/tqdm_stubs\n   :alt: Python Versions\n   :target: https://pypi.org/project/tqdm_stubs\n.. image:: https://img.shields.io/librariesio/sourcerank/pypi/tqdm_stubs\n   :alt: libraries.io sourcerank\n   :target: https://libraries.io/pypi/tqdm_stubs\n.. image:: https://img.shields.io/github/stars/charmoniumQ/tqdm-stubs?style=social\n   :alt: GitHub stars\n   :target: https://github.com/charmoniumQ/tqdm-stubs\n.. image:: https://github.com/charmoniumQ/tqdm-stubs/actions/workflows/main.yaml/badge.svg\n   :alt: CI status\n   :target: https://github.com/charmoniumQ/tqdm-stubs/actions/workflows/main.yaml\n.. image:: https://img.shields.io/github/last-commit/charmoniumQ/tqdm-stubs\n   :alt: GitHub last commit\n   :target: https://github.com/charmoniumQ/tqdm-stubs/commits\n.. image:: http://www.mypy-lang.org/static/mypy_badge.svg\n   :target: https://mypy.readthedocs.io/en/stable/\n   :alt: Checked with Mypy\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Code style: black\n\nStub type files for tqdm\n\nI found type signatures from `here`_; I put them into their own package and am writing tests.\n\n.. _`here`: https://github.com/lschmelzeisen/nasty-typeshed/blob/master/src/tqdm-stubs/__init__.pyi\n\n----------\nQuickstart\n----------\n\nIf you don't have ``pip`` installed, see the `pip install guide`_.\n\n.. _`pip install guide`: https://pip.pypa.io/en/latest/installing/\n\n.. code-block:: console\n\n    $ pip install tqdm-stubs\n",
    'author': 'Samuel Grayson',
    'author_email': 'sam+dev@samgrayson.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/charmoniumQ/tqdm-stubs',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
