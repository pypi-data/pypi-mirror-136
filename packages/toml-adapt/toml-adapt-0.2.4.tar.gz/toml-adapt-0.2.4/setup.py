# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['toml_adapt']

package_data = \
{'': ['*']}

install_requires = \
['click', 'toml']

entry_points = \
{'console_scripts': ['toml-adapt = toml_adapt.main:TomlAdapt']}

setup_kwargs = {
    'name': 'toml-adapt',
    'version': '0.2.4',
    'description': 'A very simple cli for manipulating toml files.',
    'long_description': '# toml-adapt --- Adapt toml files\n\n---\n[![PyPI Version](https://img.shields.io/pypi/v/toml-adapt.svg)](https://pypi.python.org/pypi/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/toml-adapt.svg)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/toml-adapt.svg)\n[![GitHub license](https://img.shields.io/github/license/firefly-cpp/toml-adapt.svg)](https://github.com/firefly-cpp/toml-adapt/blob/master/LICENSE)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/w/firefly-cpp/toml-adapt.svg)\n[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/firefly-cpp/toml-adapt.svg)](http://isitmaintained.com/project/firefly-cpp/toml-adapt "Average time to resolve an issue")\n[![Percentage of issues still open](http://isitmaintained.com/badge/open/firefly-cpp/toml-adapt.svg)](http://isitmaintained.com/project/firefly-cpp/toml-adapt "Percentage of issues still open")\n![GitHub contributors](https://img.shields.io/github/contributors/firefly-cpp/toml-adapt.svg)\n[![Fedora package](https://img.shields.io/fedora/v/python3-toml-adapt?color=blue&label=Fedora%20Linux&logo=fedora)](https://src.fedoraproject.org/rpms/python-toml-adapt)\n\n## Description\nWorking with TOML files is becoming inevitable during the package maintenance process in different ecosystems. Many times package maintainers must either change the version of dependency or add/remove dependencies when building their packages, due to the inconsistent base system. For example, solving this issue can be done either by using the provided patches or using sed commands. However, this\nmay be slightly time-consuming and irritating. A very simple yet user-friendly command line interface was developed in order to make this process easier.\n\n### Features\n\nCLI currently supports the following operations:\n\n- adding/removing dependencies\n- changing the  dependency version\n- changing the dependency versions of all packages concurrently\n- adding/removing/changing dev dependencies\n\n### Supported packaging tools\n\nThe following packaging tools are currently supported by this software:\n\n- poetry\n- flit\n- cargo\n- julia (partly)\n\n## Installation\n\n### pip3\n\nInstall toml-adapt with pip3:\n\n```sh\npip3 install toml-adapt\n```\n\n### Fedora Linux\n\nTo install toml-adapt on Fedora, use:\n\n```sh\n$ dnf install python-toml-adapt\n```\n\n### Usage\n\n`-a` Available actions are:\n- add\n- remove\n- change\n- add-dev\n- remove-dev\n- change-dev\n\n`-path` Specifies the path to the TOML file you wish to edit.\n\n`-dep` This option sets the name of dependency you wish to manipulate. Reserved keyword `ALL` will instead do action on all dependencies. \n\n`-ver` This option sets the version. With Python Poetry, there is reserved keyword `X`, which will become `*` (meaning it accepts any version of dependency).\n\nThe following are examples of usage:\n\n### Change dependency\n```sh\ntoml-adapt -path pyproject.toml -a change -dep niaclass -ver 0.1.0\n```\n\n### Add dependency\n```sh\ntoml-adapt -path pyproject.toml -a add -dep niaclass -ver 0.1.0\n```\n\n### Remove dependency\n```sh\ntoml-adapt -path pyproject.toml -a remove -dep niaclass -ver 0.1.0\n```\n\n### Other examples\n\nChange all existing dependencies in toml file\n```sh\ntoml-adapt -path pyproject.toml -a change -dep ALL -ver X\n```\nX represents a *\n\n### How to use it in SPEC files?\n\n```sh\n%prep\n...\n\t\n## Make dependencies consistent with Fedora dependencies\n\t\ntoml-adapt -path pyproject.toml -a change -dep ALL -ver X\n```\n\n## License\n\nThis package is distributed under the MIT License. This license can be found online at <http://www.opensource.org/licenses/MIT>.\n\n## Disclaimer\n\nThis framework is provided as-is, and there are no guarantees that it fits your purposes or that it is bug-free. Use it at your own risk!\n',
    'author': 'iztokf',
    'author_email': 'iztokf@fedoraproject.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
