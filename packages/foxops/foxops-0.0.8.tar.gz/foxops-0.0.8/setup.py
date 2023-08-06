# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['foxops']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'aiohttp>=3.8.0,<4.0.0',
 'aiopath>=0.6.10,<0.7.0',
 'dictdiffer>=0.9.0,<0.10.0',
 'pydantic>=1.9.0,<2.0.0',
 'ruamel.yaml>=0.17.20,<0.18.0',
 'structlog>=21.2.0,<22.0.0',
 'tenacity>=8.0.1,<9.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['foxops = foxops.__main__:app']}

setup_kwargs = {
    'name': 'foxops',
    'version': '0.0.8',
    'description': 'Foxops 🦊',
    'long_description': '# foxops\n\ncoming soon, stay tuned! 🦊\n',
    'author': 'Alexander Hungenberg',
    'author_email': 'alexander.hungenberg@roche.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10',
}


setup(**setup_kwargs)
