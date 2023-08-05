# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ensembleclustering',
 'ensembleclustering.tests',
 'ensembleclustering.tests.data']

package_data = \
{'': ['*'], 'ensembleclustering': ['kahypar_config/*']}

install_requires = \
['kahypar==1.1.3',
 'numpy>=1.19.5,<2.0.0',
 'pymetis==2020.1',
 'pytest>=7.1.2,<8.0.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'scipy>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'ensembleclustering',
    'version': '1.0.1',
    'description': '',
    'long_description': None,
    'author': 'Takehiro Sano',
    'author_email': 'tsano430@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
