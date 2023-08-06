# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ros', 'ros.inteface', 'ros.ip', 'ros.ip.dhcp_server', 'ros.system']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.4.0,<22.0.0', 'cattrs>=22.1.0,<23.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'rosrestpy',
    'version': '0.1.3',
    'description': 'RouterOS v7 REST API python module',
    'long_description': '# rosrestpy\n\n[![PyPi Package Version](https://img.shields.io/pypi/v/rosrestpy)](https://pypi.org/project/rosrestpy/)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/rosrestpy)](https://pypi.org/project/rosrestpy/)\n[![LICENSE](https://img.shields.io/github/license/hexatester/rosrestpy)](https://github.com/hexatester/rosrestpy/blob/main/LICENSE)\n\nRouterOS v7 REST API python module\n\n## RouterOS v7 REST API Support\n\nNot all types and methods of the RouterOS v7 REST API are supported, yet.\n\n## Installing\n\nYou can install or upgrade python-telegram-bot with:\n\n```bash\npip install rosrestpy --upgrade\n```\n\n## Example\n\n```python\nfrom ros import Ros\n\nros = Ros("https://192.168.88.1/", "admin", "")\nprint(ros.system.resource.cpu_load)\n```\n',
    'author': 'hexatester',
    'author_email': 'hexatester@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hexatester/rosrestpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
