# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypelinez']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'semantic-version>=2.8.5,<3.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['pypelinez = pypelinez.main:main']}

setup_kwargs = {
    'name': 'pypelinez',
    'version': '0.5.3',
    'description': '',
    'long_description': '# Pypelines\n\n## Description\nPython command line tool to support CI/CD for various platforms\n\n-- badges --\n\n-- images --\n\n## Installation\n\n## Usage\n\n## Support\n\n## Roadmap\n\n## Contributing\n\n## Authors and Acknowledgements\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)',
    'author': 'thecb4',
    'author_email': 'cavelle@thecb4.io',
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
