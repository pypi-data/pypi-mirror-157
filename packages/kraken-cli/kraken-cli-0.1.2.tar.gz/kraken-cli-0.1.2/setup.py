# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cli']

package_data = \
{'': ['*']}

install_requires = \
['kraken-core>=0.2.0,<0.3.0',
 'slap.core.cli>=0.3.1,<0.4.0',
 'termcolor>=1.1.0,<2.0.0',
 'types-termcolor>=1.1.5,<2.0.0']

entry_points = \
{'console_scripts': ['kraken = kraken.cli.__main__:_entrypoint']}

setup_kwargs = {
    'name': 'kraken-cli',
    'version': '0.1.2',
    'description': '',
    'long_description': '# kraken-cli\n\nThe command-line interface to the Kraken CLI.\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
