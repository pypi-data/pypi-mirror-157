# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['src', 'src.addon', 'src.ankisyncd', 'src.ankisyncd_cli']

package_data = \
{'': ['*']}

install_requires = \
['anki==2.1.49',
 'beautifulsoup4>=4.9.1,<5.0.0',
 'decorator>=4.4.2,<5.0.0',
 'distro>=1.5.0,<2.0.0',
 'markdown>=3.2.2,<4.0.0',
 'psutil>=5.7.2,<6.0.0',
 'requests>=2.24.0,<3.0.0',
 'send2trash>=1.5.0,<2.0.0',
 'webob>=1.8.6,<2.0.0']

setup_kwargs = {
    'name': 'anki-sync-server',
    'version': '2.4.0',
    'description': 'Self-hosted Anki Sync Server.',
    'long_description': None,
    'author': 'Vikash Kothary',
    'author_email': 'kothary.vikash@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
