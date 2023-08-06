# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mdbom', 'mdbom.bom', 'mdbom.md']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0', 'click>=7.1.2,<8.0.0']

entry_points = \
{'console_scripts': ['mdb = mdbom.mdbom:cli']}

setup_kwargs = {
    'name': 'mdbom',
    'version': '0.2.3',
    'description': 'Transform SBOM to Markdown',
    'long_description': '# Markdown SBOM\n\n[![ci](https://github.com/HaRo87/mdbom/workflows/ci/badge.svg)](https://github.com/HaRo87/mdbom/actions?query=workflow%3Aci)\n[![cd](https://github.com/HaRo87/mdbom/workflows/deploy/badge.svg)](https://github.com/HaRo87/mdbom/actions?query=workflow%3Adeploy)\n[![codecov](https://codecov.io/gh/HaRo87/mdbom/branch/main/graph/badge.svg?token=TGS5QA1M48)](https://codecov.io/gh/HaRo87/mdbom)\n[![documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg?style=flat)](https://HaRo87.github.io/mdbom/)\n[![pypi version](https://img.shields.io/pypi/v/mdbom.svg)](https://pypi.org/project/mdbom/)\n\nTransform Software Bill Of Materials (SBOM) to Markdown.\n\n## Requirements\n\nMdBOM requires Python 3.8 or above.\n\n## Documentation\n\nThe [documentation](https://haro87.github.io/mdbom/) is hosted on GitHub Pages.\n\n## Installation\n\nWith `pip`:\n```bash\npip install mdbom\n```\n\nWith [`pipx`](https://github.com/pipxproject/pipx):\n```bash\npython -m pip install --user pipx\n\npipx install --python python3.8 mdbom\n```\n\n## Development\n\nYou need [Task](https://taskfile.dev/#/installation).\n\nSetup your development environment:\n\n```bash\ntask setup\n```\n\n',
    'author': 'Robert Hansel',
    'author_email': 'code@fam-hansel.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://haro87.github.io/mdbom/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
