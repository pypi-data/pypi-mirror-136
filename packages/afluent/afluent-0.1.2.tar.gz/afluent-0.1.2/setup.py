# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['afluent']

package_data = \
{'': ['*']}

install_requires = \
['coverage>=6.3,<7.0', 'pytest>=5.2,<6.0']

entry_points = \
{'pytest11': ['afluent = afluent.main']}

setup_kwargs = {
    'name': 'afluent',
    'version': '0.1.2',
    'description': 'Automated Fault Localization Plugin for Pytest',
    'long_description': '# AFLuent\n\nSpectrum Based Fault Localization Plugin for PyTest\n',
    'author': 'Noor Buchi',
    'author_email': 'buchin@allegheny.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/noorbuchi/AFLuent',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
