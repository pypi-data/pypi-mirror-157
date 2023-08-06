# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easy-streamdj']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.8.1,<4.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'names>=0.3.0,<0.4.0']

setup_kwargs = {
    'name': 'easy-streamdj',
    'version': '1.1.1',
    'description': 'script for sending all youtube playlist to streamdj.app',
    'long_description': 'Works only if music requests is free.\n\n# Easy streamdj.app\nCreated for easyer send/skip tracks in streamdj.app.  \nproxy list for skip tracks from [here](https://github.com/TheSpeedX/PROXY-List)\n\n## How to install\n```bash\npip install easy-streamdj\n```\n\n## Usage examples\nget some help:\n```bash\npython -m easy-streamdj\n```\n\nsend one track:\n```bash\npython -m easy-streamdj some_channel --video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n\n```\n\nsend playlist of tracks:\n```bash\npython -m easy-streamdj some_channel --playlist "https://www.youtube.com/playlist?list=PL2aMEXnwcG3nqpr49qfCJ5vLTuxImPdme"\n```\n\nsend playlist first playlist finded on youtube:\n```bash\npython -m easy-streamdj some_channel --playlistserch "good music"\n```\n\nskip current track:\n```bash\npython -m easy-streamdj some_channel --skip\n```\n\nrun easy streamdj over tor (linux):\n```bash\nsudo systemctl start tor  # start tor service if it is not started already\ntorify python -m easy-streamdj some_channel -P "bad music" --delay 12 --author "anonymous"\n```\n\n## Install from source\nInstall [python3.10+](https://www.python.org/downloads/)\n```bash\ngit clone https://github.com/e6000000000/easy-streamdj.git\ncd easy-streamdj\npip install poetry\npoetry build\npip install dist/*.whl\n```\n',
    'author': 'a',
    'author_email': 'skipper224483@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/e9000000000/easy-streamdj',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
