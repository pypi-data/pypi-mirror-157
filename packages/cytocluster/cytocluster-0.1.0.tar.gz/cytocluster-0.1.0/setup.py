# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cytocluster', 'cytocluster.methods', 'cytocluster.tests']

package_data = \
{'': ['*'], 'cytocluster.tests': ['assets/*']}

install_requires = \
['MiniSom>=2.3.0,<3.0.0',
 'PhenoGraph>=1.5.7,<2.0.0',
 'cytoplots>=0.1.0,<0.2.0',
 'cytotools>=0.1.1,<0.2.0',
 'ensembleclustering>=1.0.1,<2.0.0',
 'hdmedians>=0.14.2,<0.15.0',
 'hnswlib>=0.6.2,<0.7.0',
 'ipython>=8.4.0,<9.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'cytocluster',
    'version': '0.1.0',
    'description': 'A package for clustering high-dimensional cytometry data in Python.',
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
