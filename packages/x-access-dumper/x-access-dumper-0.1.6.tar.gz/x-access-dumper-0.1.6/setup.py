# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['x_access_dumper']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'cchardet>=2.1.7,<3.0.0',
 'ds-store>=1.3.0,<2.0.0']

entry_points = \
{'console_scripts': ['x-access-dumper = x_access_dumper.cli:main']}

setup_kwargs = {
    'name': 'x-access-dumper',
    'version': '0.1.6',
    'description': 'Dumps everything web accessible: git repos, files from .DS_Store, sql dumps, backups, configs...',
    'long_description': '# X-Access-Dumper\n\nDumps everything web accessible: git repos, files from `.DS_Store`, sql dumps, backups, configs...\n\nUse asdf or pyenv to install latest python version.\n\nInstall:\n\n```bash\n$ pip install x-access-dumper\n$ pipx install x-access-dumper\n```\n\nUsage:\n\n```\n$ x-access-dumper -h\n$ x-access-dumper url1 url2 url3\n$ x-access-dumper < urls.txt\n$ command | x-access-dumper\n$ x-access-dumper -vv https://target 2> log.txt\n```\n\n# TODO:\n\n- <s>exclude images and media files by default</s> \n',
    'author': 'tz4678',
    'author_email': 'tz4678@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tz4678/x-access-dumper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
