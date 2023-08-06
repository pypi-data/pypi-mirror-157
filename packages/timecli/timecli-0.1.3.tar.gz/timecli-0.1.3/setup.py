# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['timecli', 'timecli.commands', 'timecli.core']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10.2,<0.11.0', 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['timecli = timecli.main:app']}

setup_kwargs = {
    'name': 'timecli',
    'version': '0.1.3',
    'description': '',
    'long_description': '# Time\n\n## Description\nThe simple time cli.\n',
    'author': 'gelleson',
    'author_email': 'go.gelleson@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
