# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydle',
 'pydle.features',
 'pydle.features.ircv3',
 'pydle.features.rfc1459',
 'pydle.features.rpl_whoishost',
 'pydle.utils']

package_data = \
{'': ['*']}

extras_require = \
{'sasl': ['pure-sasl>=0.6.2,<0.7.0']}

entry_points = \
{'console_scripts': ['pydle = pydle.utils.run:main',
                     'pydle-irccat = pydle.utils.irccat:main']}

setup_kwargs = {
    'name': 'pydle',
    'version': '1.0.0',
    'description': 'A compact, flexible, and standards-abiding IRC library for python3.',
    'long_description': None,
    'author': 'Shiz',
    'author_email': 'hi@shiz.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Shizmob/pydle',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
