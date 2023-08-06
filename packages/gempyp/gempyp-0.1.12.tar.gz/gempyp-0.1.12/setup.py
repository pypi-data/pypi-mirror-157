# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gempyp',
 'gempyp.config',
 'gempyp.data_compare',
 'gempyp.data_compare.common',
 'gempyp.data_compare.configurator',
 'gempyp.data_compare.core',
 'gempyp.data_compare.data',
 'gempyp.data_compare.report',
 'gempyp.data_compare.tools',
 'gempyp.engine',
 'gempyp.engine.executors',
 'gempyp.libs',
 'gempyp.libs.enums',
 'gempyp.libs.exceptions',
 'gempyp.pyprest',
 'gempyp.reporter']

package_data = \
{'': ['*'], 'gempyp.data_compare': ['config/*']}

install_requires = \
['certifi>=2022.6.15,<2023.0.0',
 'cffi>=1.15.0,<2.0.0',
 'charset-normalizer>=2.0.12,<3.0.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'cryptography>=37.0.2,<38.0.0',
 'humanfriendly>=10.0,<11.0',
 'idna>=3.3,<4.0',
 'lxml>=4.9.0,<5.0.0',
 'ntlm-auth>=1.5.0,<2.0.0',
 'numpy>=1.22.4,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'pycparser>=2.21,<3.0',
 'pyreadline3>=3.4.1,<4.0.0',
 'pytest>=6.2.4,<7.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'pytz>=2022.1,<2023.0',
 'requests-ntlm>=1.1.0,<2.0.0',
 'requests>=2.28.0,<3.0.0',
 'six>=1.16.0,<2.0.0',
 'urllib3>=1.26.9,<2.0.0']

entry_points = \
{'console_scripts': ['gempyp = gempyp.gemPyp:main']}

setup_kwargs = {
    'name': 'gempyp',
    'version': '0.1.12',
    'description': 'An ecosystem of libraries useful for software development',
    'long_description': '# GEMPYP\n\n[![Python](https://img.shields.io/badge/python-3.7-blue)]()\n\n## Installation\n\n```powershell\n$ pip install gempyp\n```\n\n## Features\n\n- TODO\n\n## Dependencies\n\n- TODO\n\n## Usage\n\n- TODO\n\n## Documentation\n\nThe official documentation is hosted on Read the Docs: https://gempyp.readthedocs.io/en/latest/\n\n## Contributors\n\nWe welcome and recognize all contributions. You can see a list of current contributors in the [contributors tab](https://github.com/Gemini-Solutions/gempyp/).\n\n### Credits\n\nThis package was created with Cookiecutter and the UBC-MDS/cookiecutter-ubc-mds project template, modified from the [pyOpenSci/cookiecutter-pyopensci](https://github.com/pyOpenSci/cookiecutter-pyopensci) project template and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage).\n',
    'author': 'Gemini Solutions-QA',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Gemini-Solutions/gempyp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.0,<4.0.0',
}


setup(**setup_kwargs)
