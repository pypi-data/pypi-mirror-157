# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simpletyper',
 'simpletyper.events',
 'simpletyper.utils',
 'simpletyper.widgets']

package_data = \
{'': ['*'], 'simpletyper': ['words/*']}

install_requires = \
['textual>=0.1.18,<0.2.0']

entry_points = \
{'console_scripts': ['simpletyper = simpletyper.__init__:main']}

setup_kwargs = {
    'name': 'simpletyper',
    'version': '0.1.3',
    'description': 'Typing speed tester powered by Textual',
    'long_description': None,
    'author': 'Wilson Oh',
    'author_email': 'oh.wilson123@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
