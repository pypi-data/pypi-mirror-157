# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyrosimple',
 'pyrosimple.daemon',
 'pyrosimple.data.config',
 'pyrosimple.io',
 'pyrosimple.job',
 'pyrosimple.scripts',
 'pyrosimple.torrent',
 'pyrosimple.ui',
 'pyrosimple.util']

package_data = \
{'': ['*'],
 'pyrosimple': ['data/htdocs/*',
                'data/htdocs/css/*',
                'data/htdocs/img/*',
                'data/htdocs/js/*',
                'data/img/*',
                'data/screenlet/*',
                'data/screenlet/themes/blueish/*',
                'data/screenlet/themes/default/*'],
 'pyrosimple.data.config': ['color-schemes/*',
                            'rtorrent.d/*',
                            'templates/*',
                            'templates/conky/*']}

install_requires = \
['Jinja2>=3.1.0,<4.0.0',
 'bencode.py>=4.0.0,<5.0.0',
 'dynaconf[toml]>=3.1.0,<4.0.0',
 'parsimonious>=0.9.0,<0.10.0',
 'prometheus-client>=0.14.1,<0.15.0',
 'prompt-toolkit>=3.0.30,<4.0.0',
 'python-daemon>=2.3.0,<3.0.0']

extras_require = \
{':python_version < "3.9"': ['importlib-resources>=5.4.0,<6.0.0'],
 'torque': ['APScheduler>=3.9.0,<4.0.0', 'pyinotify>=0.9.6,<0.10.0']}

entry_points = \
{'console_scripts': ['chtor = pyrosimple.scripts.chtor:run',
                     'lstor = pyrosimple.scripts.lstor:run',
                     'mktor = pyrosimple.scripts.mktor:run',
                     'pyroadmin = pyrosimple.scripts.pyroadmin:run',
                     'pyrotorque = pyrosimple.scripts.pyrotorque:run',
                     'rtcontrol = pyrosimple.scripts.rtcontrol:run',
                     'rtxmlrpc = pyrosimple.scripts.rtxmlrpc:run']}

setup_kwargs = {
    'name': 'pyrosimple',
    'version': '2.0.0rc2',
    'description': '',
    'long_description': "# pyrosimple\n\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/kannibalox/pyrosimple/Pylint)](https://github.com/kannibalox/pyrosimple/actions/workflows/pylint.yml)\n[![PyPI](https://img.shields.io/pypi/v/pyrosimple)](https://pypi.org/project/pyrosimple/)\n![PyPI -\tPython Version](https://img.shields.io/pypi/pyversions/pyrosimple)\n\nA overhauled Python 3 fork  of the [pyrocore tools](https://github.com/pyroscope/pyrocore), for working with the [rTorrent client](https://github.com/rakshasa/rtorrent).\n\n## Installation\n\n```bash\npip install pyrosimple\n```\n\nSee the [documentation for usage](https://kannibalox.github.io/pyrosimple/). If you've used rtcontrol/rtxmlrpc before, you should feel right at home.\n\n## What's the point of this?\n\nThe pyrocore tools are great, but being stuck on python 2, along with the complicated install procedure made integrating both the tools and the code into other processes very painful.\n\n## Differences from pyrocore\n\nThe following lists are not exhaustive, and don't cover many of the internal improvements and refactoring.\n\n- Only supports python 3 and rtorrent 0.9.8+ (0.9.6/0.9.7 should still work just fine, but aren't officially supported)\n- Simpler poetry-based build/install system\n- Everything in one package (no separate pyrobase)\n  - Use external lib for bencode\n\n### New features\n- Multi-instance support for rtcontrol/rtxmlrpc\n- Replaced Tempita with jinja2\n- Support for JSON-RPC (only implemented by https://github.com/jesec/rtorrent)\n- pyrotorque job to move torrents between hosts\n- pyrotorque job to move torrent paths\n",
    'author': 'kannibalox',
    'author_email': 'kannibalox@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kannibalox/pyrosimple',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
