# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splink_cluster_studio']

package_data = \
{'': ['*'], 'splink_cluster_studio': ['css/*', 'jinja/*', 'js_lib/*']}

install_requires = \
['Jinja2>=3.0.2,<4.0.0']

setup_kwargs = {
    'name': 'splink-cluster-studio',
    'version': '0.1.1',
    'description': 'Create an interactive webpage to visualise clusters',
    'long_description': None,
    'author': 'Robin Linacre',
    'author_email': 'robinlinacre@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
