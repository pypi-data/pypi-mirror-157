# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['napr',
 'napr.apps',
 'napr.apps.coconut',
 'napr.apps.coconut.terpene',
 'napr.apps.coconut.terpene.tests',
 'napr.data',
 'napr.data.tests',
 'napr.evaluation',
 'napr.evaluation.tests',
 'napr.hyperopt',
 'napr.hyperopt.tests',
 'napr.plotting',
 'napr.plotting.tests',
 'napr.utils',
 'napr.utils.tests']

package_data = \
{'': ['*']}

install_requires = \
['keras-tuner>=1.1.2,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'requests>=2.27.1,<3.0.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'tqdm>=4.64.0,<5.0.0',
 'xgboost>=1.6.1,<2.0.0']

extras_require = \
{':python_version >= "3.8" and python_version < "3.11"': ['scipy>=1.8.0,<2.0.0'],
 ':python_version >= "3.9" and python_version < "3.11"': ['tensorflow>=2.9.1,<3.0.0']}

setup_kwargs = {
    'name': 'napr',
    'version': '0.1.5',
    'description': 'Machine learning meets natural products',
    'long_description': None,
    'author': 'Morteza Hosseini',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
