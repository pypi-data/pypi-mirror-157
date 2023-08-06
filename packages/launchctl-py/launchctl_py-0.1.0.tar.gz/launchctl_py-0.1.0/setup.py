# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['launchctl_py']

package_data = \
{'': ['*']}

install_requires = \
['tabulate>=0.8.9']

entry_points = \
{'console_scripts': ['launchctl_py = launchctl_py:cli.main',
                     'launchctl_python = launchctl_py:cli.main',
                     'lpy = launchctl_py:cli.main']}

setup_kwargs = {
    'name': 'launchctl-py',
    'version': '0.1.0',
    'description': 'Quickly create simple background services (i.e., launchctl agents) for macOS.',
    'long_description': '# Launchctl-Py\n\n🚀 Quickly create simple background services (i.e., launchctl agents) for macOS in Python.\n\n[![Supported Python versions](https://img.shields.io/badge/Python-%3E=3.7-blue.svg?logo=python)](https://www.python.org/downloads/) [![PEP8](https://img.shields.io/badge/Code%20style-PEP%208-orange.svg?logo=python)](https://www.python.org/dev/peps/pep-0008/) ![platform](https://img.shields.io/badge/Platform-macOS-green.svg?logo=apple)\n\n\n## Requirements\n- 🐍 [python>=3.7](https://www.python.org/downloads/)\n\n## ⬇️ Installation\n\n```sh\npip install launchctl-py\n```\n\n## ⌨️ Usage\n\n```\nusage: lpy [-h] [-c] [-s]\n\noptional arguments:\n  -h, --help    show this help message and exit\n  -c, --create  Create a new launchctl agent\n  -s, --status  Get the status of the agents you created\n```\n\n\n## 💡 Misc.\n\nOptional: if you want the domain name of your agents to be something other than `local` (default), run:\n```sh\nlaunchctl setenv DEFAULT_DOMAIN "ReplaceMe"\necho \'setenv DEFAULT_DOMAIN ReplaceMe\' >> ~/.conf.launchd\n```\n',
    'author': 'Alyetama',
    'author_email': 'malyetama@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
