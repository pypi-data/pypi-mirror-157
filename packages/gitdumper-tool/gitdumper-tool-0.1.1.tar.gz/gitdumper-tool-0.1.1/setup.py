# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitdumper_tool']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0', 'aiohttp>=3.8.1,<4.0.0', 'cchardet>=2.1.7,<3.0.0']

entry_points = \
{'console_scripts': ['gitdumper = gitdumper_tool.cli:main']}

setup_kwargs = {
    'name': 'gitdumper-tool',
    'version': '0.1.1',
    'description': 'Git Dumper Tool',
    'long_description': '# Git Dumper\n\nGit Dumper Tool.\n\nUse asdf or pyenv to install latest python version.\n\n```bash\n$ pip install gitdumper-tool\n$ pipx install gitdumper-tool\n$ gitdumper -h\n$ gitdumper url [... url]\n$ gitdumper < urls.txt\n$ girdumper url 2> err.log\n```\n',
    'author': 'tz4678',
    'author_email': 'tz4678@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tz4678/gitdumper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
