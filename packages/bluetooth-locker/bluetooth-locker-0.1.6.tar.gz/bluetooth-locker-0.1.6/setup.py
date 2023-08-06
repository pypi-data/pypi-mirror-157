# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bluetooth_locker']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['bluetooth-locker = bluetooth_locker.app:main']}

setup_kwargs = {
    'name': 'bluetooth-locker',
    'version': '0.1.6',
    'description': 'A bluetooth based locker',
    'long_description': '# Bluetooth Locker\n<p>\n    <a href="https://pypi.org/project/bluetooth-locker/" target="_blank">\n        <img src="https://img.shields.io/pypi/v/bluetooth-locker" />\n    </a>\n    <a href="https://github.com/leng-yue/bluetooth-locker/actions/workflows/ci.yml" target="_blank">\n        <img src="https://img.shields.io/github/workflow/status/leng-yue/bluetooth-locker/CI?label=check" />\n    </a>\n    <img src="https://img.shields.io/github/license/leng-yue/bluetooth-locker" />\n    <a href="https://pepy.tech/project/bluetooth-locker" target="_blank">\n        <img src="https://pepy.tech/badge/bluetooth-locker" />\n    </a>\n</p>\n\nA simple bluetooth based locker that lock and unlock your linux desktop automatically.\n\n## How to use\n\nYou need to have `libbluetooth-dev` in your system. \n\n```shell\n# Simple run\nbluetooth-locker -d xx:xx:xx:xx:xx:xx\n\n# Multiple devices\nbluetooth-locker -d xx:xx:xx:xx:xx:xx -d xx:xx:xx:xx:xx:aa\n\n# Install service\nsudo bluetooth-locker -d xx:xx:xx:xx:xx:xx --install\n\n# Uninstall service\nsudo bluetooth-locker -d xx:xx:xx:xx:xx:xx --uninstall\n```\n\n## [Optional] Arduino Bluetooth Key\n\nThough we recommand you to use your phone as the key.\n\nHere is a simple arduino bluetooth server implementation.\n',
    'author': 'leng-yue',
    'author_email': 'lengyue@lengyue.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/leng-yue/bluetooth-locker',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
