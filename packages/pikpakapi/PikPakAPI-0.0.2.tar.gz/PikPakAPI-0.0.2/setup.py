# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pikpakapi']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'pikpakapi',
    'version': '0.0.2',
    'description': 'PikPakAPI',
    'long_description': '# PikPakAPI\n# PikPakAPI\n',
    'author': 'Quan666',
    'author_email': 'i@Rori.eMail',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Quan666/PikPakAPI',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
