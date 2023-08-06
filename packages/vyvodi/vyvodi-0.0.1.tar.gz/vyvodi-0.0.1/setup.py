# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vyvodi', 'vyvodi.layers']

package_data = \
{'': ['*']}

install_requires = \
['keras>=2.6.0,<2.7.0',
 'tensorflow-probability>=0.13.0rc0,<0.14.0',
 'tensorflow>=2.6.0,<2.7.0']

setup_kwargs = {
    'name': 'vyvodi',
    'version': '0.0.1',
    'description': 'custom tensorflow tools',
    'long_description': '# vyvodi\n',
    'author': 'nickolasgryga',
    'author_email': 'nick@gryga.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vyvodi/vyvodi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
