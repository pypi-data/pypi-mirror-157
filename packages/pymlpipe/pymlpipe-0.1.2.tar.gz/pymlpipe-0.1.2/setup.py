# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymlpipe', 'pymlpipe.utils']

package_data = \
{'': ['*'],
 'pymlpipe': ['.git/*',
              '.git/hooks/*',
              '.git/info/*',
              '.git/logs/*',
              '.git/logs/refs/heads/*',
              '.git/logs/refs/remotes/origin/*',
              '.git/objects/pack/*',
              '.git/refs/heads/*',
              '.git/refs/remotes/origin/*',
              'static/*',
              'templates/*']}

install_requires = \
['Flask-API>=3.0.post1,<4.0',
 'Flask>=2.1.2,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'pandas>=1.4.3,<2.0.0',
 'pytest==5.2',
 'sklearn>=0.0,<0.1']

entry_points = \
{'console_scripts': ['pymlpipeui = pymlpipe.pymlpipeUI:start_ui']}

setup_kwargs = {
    'name': 'pymlpipe',
    'version': '0.1.2',
    'description': 'PyMLpipe is a Python library for ease Machine Learning Model monitering and Deployment.',
    'long_description': None,
    'author': 'Indresh Bhattacharya',
    'author_email': 'indresh2neel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
