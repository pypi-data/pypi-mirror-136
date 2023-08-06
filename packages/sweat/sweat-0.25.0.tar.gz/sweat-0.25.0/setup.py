# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sweat',
 'sweat.examples',
 'sweat.hrm',
 'sweat.io',
 'sweat.metrics',
 'sweat.pdm']

package_data = \
{'': ['*'], 'sweat.examples': ['data/*']}

install_requires = \
['fitparse>=1.1.0,<2.0.0',
 'lmfit>=1.0.0,<2.0.0',
 'matplotlib>=3.3.4,<4.0.0',
 'pandas>=1.0.3,<2.0.0',
 'pydantic>=1.4,<2.0',
 'pyyaml>=6.0.0,<7.0.0',
 'requests>=2.23.0,<3.0.0',
 'scikit-learn>=0.23.1',
 'scipy>=1.4.1,<2.0.0',
 'stravalib>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'sweat',
    'version': '0.25.0',
    'description': 'Workout analysis',
    'long_description': '# Sweatpy\n\n[![Downloads](https://pepy.tech/badge/sweat)](https://pepy.tech/project/sweat)\n\n> :warning: **Sweatpy is currently undergoing major revisions which will result in deprecations and backwards incompatible changes. We recommend pinning your sweatpy dependency in your requirements.txt file (e.g. `sweat==0.19.0`).**\n\nDocumentation can be found [here](https://sweatpy.gssns.io).\n\n## Contributors\n[Maksym Sladkov](https://github.com/sladkovm)\n[Aart Goossens](https://github.com/AartGoossens)\n\n## License\nSee [LICENSE](LICENSE) file.\n',
    'author': 'Aart Goossens',
    'author_email': 'aart@goossens.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/goldencheetah/sweatpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
