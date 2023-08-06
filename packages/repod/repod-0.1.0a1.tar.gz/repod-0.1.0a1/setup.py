# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['repod',
 'repod.cli',
 'repod.common',
 'repod.config',
 'repod.files',
 'repod.repo',
 'repod.repo.management',
 'repod.repo.package',
 'repod.version']

package_data = \
{'': ['*'], 'repod': ['templates/*']}

install_requires = \
['Jinja2>=3.0.0,<4.0.0',
 'aiofiles>=0.8.0,<0.9.0',
 'email-validator>=1.2.1,<2.0.0',
 'orjson>=3.6.6,<4.0.0',
 'pydantic>=1.8.1,<2.0.0',
 'python-magic>=0.4.26,<0.5.0',
 'pyzstd>=0.15.2,<0.16.0',
 'subprocess-tee>=0.3.5,<0.4.0',
 'tomli>=2.0.0,<3.0.0']

extras_require = \
{'vercmp': ['pyalpm[vercmp]>=0.10.6,<0.11.0']}

entry_points = \
{'console_scripts': ['repod-file = repod.cli:repod_file']}

setup_kwargs = {
    'name': 'repod',
    'version': '0.1.0a1',
    'description': 'Tooling to maintain binary package repositories for Linux distributions using the pacman package manager',
    'long_description': "# repod\nThis project contains tooling to maintain binary package repositories for Linux\ndistributions using the [pacman](https://archlinux.org/pacman/) package manager.\n\nThe latest documentation can be found at\n[repod.archlinux.page](https://repod.archlinux.page).\n\n**NOTE**: *Repod is still alpha grade software and as such has not yet reached\nits targetted feature set and has not been thoroughly tested in the field. It\nshould not be used in a production environment!*\n\n## Installation\n\nThis project is Python based and uses [poetry](https://python-poetry.org/) for\nits development.\n\nTo create sdist tarball and wheel run\n\n```\npoetry build\n```\n\nTo install the resulting wheel using `pip` run\n\n```\npip install dist/*.whl\n```\n\n## Documentation\n\nThe user facing documentation of repod can be found in [docs](docs/) and is\nbuilt using\n\n```\ntox -e docs\n```\n\n## Contributing\n\nRead our [contributing guide](CONTRIBUTING.md) to learn more about how to\nprovide fixes or improvements for the code and documentation.\n\n## License\n\nRepod's code is licensed under the terms of the **GPL-3.0-or-later** (see\n[LICENSE](LICENSE)) and its documentation is licensed under the terms of the\n**GFDL-1.3-or-later** (see [docs/LICENSE](docs/LICENSE)).\n",
    'author': 'Arch Linux',
    'author_email': 'arch-projects@lists.archlinux.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.archlinux.org/archlinux/repod',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
