# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['NoobStuffs',
 'NoobStuffs.libdatetime',
 'NoobStuffs.libformatter',
 'NoobStuffs.liblogging',
 'NoobStuffs.libpasty']

package_data = \
{'': ['*']}

install_requires = \
['pytz>=2022.1,<2023.0', 'requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'noobstuffs',
    'version': '1.0.2',
    'description': 'Python Library for PrajjuS Projects',
    'long_description': '# NoobStuffs\n\n[![PyPi version](https://img.shields.io/pypi/v/noobstuffs)](https://pypi.org/project/noobstuffs/)\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e73fc5d0a6b64bb8a6c286f88c1dc590)](https://www.codacy.com/gh/PrajjuS/NoobStuffs/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=PrajjuS/NoobStuffs&amp;utm_campaign=Badge_Grade)\n\n>Python3 library which consists of codes that are frequently used for my personal projects\n\n## Installation\n\n```\npip install noobstuffs\n```\n\n## Credits\n\nInspired by [sebaubuntu_libs](https://github.com/SebaUbuntu/sebaubuntu_libs)\n',
    'author': 'PrajjuS',
    'author_email': 'theprajjus@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PrajjuS/NoobStuffs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
