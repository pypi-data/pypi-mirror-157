# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ghpages']

package_data = \
{'': ['*']}

install_requires = \
['pycommando>=2.1.3,<3.0.0']

entry_points = \
{'console_scripts': ['ghpages = ghpages.main:main']}

setup_kwargs = {
    'name': 'ghpages',
    'version': '0.0.1',
    'description': 'Publish files to a gh-pages branch on GitHub',
    'long_description': 'None',
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
