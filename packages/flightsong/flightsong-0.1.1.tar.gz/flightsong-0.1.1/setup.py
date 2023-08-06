# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flightsong']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0', 'rich>=12.4.4,<13.0.0', 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['flightsong = flightsong.main:app']}

setup_kwargs = {
    'name': 'flightsong',
    'version': '0.1.1',
    'description': '',
    'long_description': '# Flightsong cli\n\n```bash\npython -m pip install -r requirements.txt\nexport SHOPIFY_TOKEN=your-token-here\npython -m flightsong\n```\n',
    'author': 'Jón Levy',
    'author_email': 'nonni@nonni.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
