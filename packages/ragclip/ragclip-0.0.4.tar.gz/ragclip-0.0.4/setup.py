# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ragclip']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.1.4,<2.0.0']

entry_points = \
{'console_scripts': ['rag = ragclip.clip:main']}

setup_kwargs = {
    'name': 'ragclip',
    'version': '0.0.4',
    'description': '',
    'long_description': '# RagCLIP\n\n*Rag command line proxy.*\n',
    'author': 'Mark Raleson',
    'author_email': 'markraleson@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mraleson/ragclip.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
