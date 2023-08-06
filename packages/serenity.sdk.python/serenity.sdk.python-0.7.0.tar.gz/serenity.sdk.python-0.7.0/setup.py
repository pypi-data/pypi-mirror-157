# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src/python'}

packages = \
['serenity_sdk']

package_data = \
{'': ['*']}

install_requires = \
['azure-identity>=1.10.0,<2.0.0', 'cryptography==37.0.2', 'fire>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'serenity.sdk.python',
    'version': '0.7.0',
    'description': 'Python SDK for the Serenity digital asset risk API',
    'long_description': "## Serenity SDK - Python\n\n### Introduction\n\nThe Serenity digital asset risk platform exposes all functionality via an API -- currently REST only.\n\nAlthough it's possible to call the API with simple HTTP client code in most any modern language, there\nare conventions that need to be followed -- especially for authentication and authorization -- and to\nmake it easier we have provided this lightweight SDK.\n\n### Learning more\n\nAt this time the API and its documentation are only available to members of our private beta, via\ntheir personal Serenity Developer Portal, e.g. https://developer.$client.cloudwall.network.",
    'author': 'Cloudwall DevSecOps',
    'author_email': 'support@cloudwall.capital',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
