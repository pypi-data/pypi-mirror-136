# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['siwe_auth']

package_data = \
{'': ['*']}

install_requires = \
['pytz>=2021.3,<2022.0', 'siwe>=0.1.2,<0.2.0', 'web3>=5.26.0,<6.0.0']

setup_kwargs = {
    'name': 'flask-siwe-auth',
    'version': '0.1.0',
    'description': 'Custom Flask authentication using Sign-In with Ethereum (EIP-4361), a custom wallet user model, and authorization via on-chain attributes.',
    'long_description': '# django-siwe-auth\nComing soon.\n',
    'author': 'Payton Garland',
    'author_email': 'payton.r.g@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/payton/flask-siwe-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
