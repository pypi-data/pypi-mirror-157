# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['signed_pickle']

package_data = \
{'': ['*']}

extras_require = \
{'lz4': ['lz4']}

setup_kwargs = {
    'name': 'signed-pickle',
    'version': '0.1.0',
    'description': 'Description',
    'long_description': '# Signed Pickle\n',
    'author': 'Daniel Sullivan',
    'author_email': 'mumblepins@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mumblepins/signed-pickle/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
