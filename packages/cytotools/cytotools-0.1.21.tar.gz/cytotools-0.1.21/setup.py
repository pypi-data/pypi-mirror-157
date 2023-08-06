# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cytotools', 'cytotools.tests']

package_data = \
{'': ['*']}

install_requires = \
['FlowIO>=1.0.1,<2.0.0',
 'FlowUtils>=1.0.0,<2.0.0',
 'KDEpy>=1.1.0,<2.0.0',
 'Shapely>=1.8.2,<2.0.0',
 'Sphinx>=5.0.2,<6.0.0',
 'alphashape>=1.3.1,<2.0.0',
 'bson>=0.5.10,<0.6.0',
 'coverage>=6.4.1,<7.0.0',
 'detecta>=0.0.5,<0.0.6',
 'ipython>=8.4.0,<9.0.0',
 'numpy>=1.22.4,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'phate>=1.0.8,<2.0.0',
 'polars>=0.13.49,<0.14.0',
 'pyarrow>=8.0.0,<9.0.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'pytest>=7.1.2,<8.0.0',
 's3fs>=2022.5.0,<2023.0.0',
 'scikit-fda>=0.7.1,<0.8.0',
 'scikit-learn>=1.0.1,<1.1.0',
 'sphinx-rtd-theme>=1.0.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'umap-learn>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'cytotools',
    'version': '0.1.21',
    'description': 'A small package of utilities for analysis of cytometry data in Python',
    'long_description': None,
    'author': 'burtonrj',
    'author_email': 'burtonrj@cardiff.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
