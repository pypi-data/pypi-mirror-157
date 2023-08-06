# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multiauth',
 'multiauth.providers',
 'multiauth.types',
 'multiauth.types.providers']

package_data = \
{'': ['*']}

install_requires = \
['Authlib>=1.0.1,<2.0.0',
 'PyJWT>=2.4.0,<3.0.0',
 'graphql-core>=3.2.1,<4.0.0',
 'pycognito>=2022.5.0,<2023.0.0',
 'pydash>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'py-multiauth',
    'version': '1.1.2',
    'description': 'Python package to interact with multiple authentication services',
    'long_description': '# py-multiauth ![PyPI](https://img.shields.io/pypi/v/py-multiauth) [![codecov](https://codecov.io/gh/Escape-Technologies/py-multiauth/branch/main/graph/badge.svg?token=NL148MNKAE)](https://codecov.io/gh/Escape-Technologies/py-multiauth)\n\n[![CI](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/ci.yaml/badge.svg)](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/ci.yaml) [![CD](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/cd.yaml/badge.svg)](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/cd.yaml)\n\n![PyPI - License](https://img.shields.io/pypi/l/py-multiauth) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-multiauth)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/py-multiauth)\n\n[View it on pypi!](https://pypi.org/project/py-multiauth/)\n\n## Installation\n\n```bash\npip install py-multiauth\n```\n\n```python\nfrom multiauth import ...\n```\n\n## Supported methods\n\n|Name     |Authenticate|Refresh|Extra    |\n|---------|:----------:|:-----:|---------|\n|`API_KEY`|✓           |       |         |\n|`AWS`    |✓           |✓      |Signature|\n|`BASIC`  |✓           |       |         |\n|`REST`   |✓           |✓      |         |\n|`DIGEST` |✓           |       |         |\n|`GRAPHQL`|✓           |       |         |\n|`HAWK`   |✓           |       |         |\n|`MANUAL` |✓           |       |         |\n|`OAUTH`  |✓           |✓      |         |\n',
    'author': 'Escape Technologies SAS',
    'author_email': 'ping@escape.tech',
    'maintainer': 'Antoine Carossio',
    'maintainer_email': 'antoine@escape.tech',
    'url': 'https://escape.tech/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
