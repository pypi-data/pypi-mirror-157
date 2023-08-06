# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypers']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'dnspython>=2.2.1,<3.0.0',
 'hachoir>=3.1.3,<4.0.0',
 'httpx>=0.22,<0.24',
 'motor>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'pypers',
    'version': '1.2.2',
    'description': 'A utilities module made for personal use, has small snippets which I use in many projects.',
    'long_description': '# pypers\n\n<p align="center">\n    <a href="https://pypi.org/project/PyPers/"><img src="https://img.shields.io/pypi/v/PyPers" alt="PyPI"></a>\n    <a href="https://github.com/Divkix/PyPers/actions"><img src="https://github.com/Divkix/PyPers/workflows/CI%20%28pip%29/badge.svg" alt="CI (pip)"></a>\n    <a href="https://pypi.org/project/pypers/"><img src="https://img.shields.io/pypi/wheel/PyPers.svg" alt="PyPI - Wheel"></a>\n    <a href="https://pypi.org/project/pypers/"><img src="https://img.shields.io/pypi/pyversions/PyPers.svg" alt="Supported Python Versions"></a>\n    <a href="https://pepy.tech/project/PyPers"><img src="https://pepy.tech/badge/PyPers" alt="Downloads"></a>\n</p>\n\nPackage with helper scripts.\n\nContains some helper function which make up its name: python+helpers = pypers.\n\nRead the docs:\n\nhttps://pypers.divkix.me\n\n\n[![Sponsor](https://www.datocms-assets.com/31049/1618983297-powered-by-vercel.svg)](https://vercel.com/?utm_source=divideprojects&utm_campaign=oss)\n',
    'author': 'Divkix',
    'author_email': 'techdroidroot@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypers.divkix.me',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
