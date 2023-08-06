# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simpletyper']

package_data = \
{'': ['*'], 'simpletyper': ['words/*']}

install_requires = \
['pyfiglet>=0.8.post1,<0.9',
 'requests>=2.28.1,<3.0.0',
 'textual>=0.1.18,<0.2.0']

setup_kwargs = {
    'name': 'simpletyper',
    'version': '0.1.1',
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
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
