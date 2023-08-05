# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tok_det_metric']

package_data = \
{'': ['*']}

install_requires = \
['datasets>=2.3.2,<3.0.0',
 'more-itertools>=8.13.0,<9.0.0',
 'numpy>=1.23.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'tok-det-metric',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Aneta Melisa Stal',
    'author_email': 'melisa@writer.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
