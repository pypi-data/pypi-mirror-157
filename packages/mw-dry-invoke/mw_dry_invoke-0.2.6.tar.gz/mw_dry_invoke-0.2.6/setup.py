# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mw_dry_invoke', 'tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mw-dry-invoke',
    'version': '0.2.6',
    'description': 'Common Invoke tasks.',
    'long_description': '\nCommon Invoke tasks\n\n* Free software: MIT License\n\nFeatures\n--------\n\n* TODO\n\n\nCredits\n-------\n\nThis package was created with Cookiecutter_ and the `midwatch/cc-py3-pkg`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`midwatch/cc-py3-pkg`: https://github.com/midwatch/cc-py3-pkg\n',
    'author': 'Justin Stout',
    'author_email': 'midwatch@jstout.us',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/midwatch/mw_dry_invoke',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
