# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lessmore_test', 'lessmore_test.code_block']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'lessmore-test.code-block',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'marklidenberg',
    'author_email': 'marklidenberg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
