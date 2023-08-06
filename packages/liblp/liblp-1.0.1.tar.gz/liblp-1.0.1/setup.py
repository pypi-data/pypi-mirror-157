# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['liblp', 'liblp.include', 'liblp.partition_tools']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['lpunpack = liblp.partition_tools.lpunpack:main']}

setup_kwargs = {
    'name': 'liblp',
    'version': '1.0.1',
    'description': 'Android logical partitions library ported from C++ to Python',
    'long_description': '# liblp\n\n[![PyPi version](https://img.shields.io/pypi/v/liblp)](https://pypi.org/project/liblp/)\n\nAndroid logical partitions library ported from C++ to Python\n\nRequires Python 3.8 or greater\n\n## Installation\n\n```sh\npip3 install liblp\n```\n\n## Instructions\n\n```sh\n# Launch lpunpack\n$ liblp\n```\n\n## License\n\n```\n#\n# Copyright (C) 2022 Sebastiano Barezzi\n#\n# SPDX-License-Identifier: Apache-2.0\n#\n```\n',
    'author': 'Sebastiano Barezzi',
    'author_email': 'barezzisebastiano@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SebaUbuntu/liblp',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
