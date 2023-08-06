# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['comiks', 'comiks.provider']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'fastDamerauLevenshtein>=1.0.7,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['comiks = comiks.run:main']}

setup_kwargs = {
    'name': 'comiks',
    'version': '1.0.0',
    'description': 'Retrieve authors informations from commits.',
    'long_description': "# Comiks\n\nComiks is a command line tool to retrieve authors informations (names and emails) in the repositories commits of a given user.\n\n![Heading illustration](https://raw.githubusercontent.com/b0oml/Comiks/master/doc/heading.png)\n\n## Installation\n\n```shell\n$ pip install git+https://github.com/b0oml/Comiks\n```\n\n## Configuration\n\nThe first time `comiks` runs, it will generate a config file `.config/comiks/config.toml` in your home directory. This will be the default configuration file used when using comiks.\n\nBy default, only Github provider is enabled, other providers needs an API key/access token. To enable and configure others providers, you can update the configuration file in your home directory.\n\nIt is also possible to load the configuration file from another path with option `-c, --config`.\n\n```shell\n$ comiks -c ./path/to/config.toml username\n```\n\nIf you wan to create your own configuration file, you can take example on [this one](./comiks/config.toml).\n\n## Usage\n\n```shell\n$ comiks --help\nusage: comiks [-h] [-c CONFIG] [-l HIGHLIGHT] [-p TAGS] [-sb] username\n\nRetrieve authors informations from commits.\n\npositional arguments:\n  username              Username for which to scan commits.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -c CONFIG, --config CONFIG\n                        Custom config file (default is ~/.config/comiks/config.toml).\n  -l HIGHLIGHT, --highlight HIGHLIGHT\n                        Strings to highlight in output, separated by a comma (default is username).\n  -p TAGS, --providers TAGS\n                        Comma-sperated list of tags to select which providers to enable (default is in\n                        config).\n  -sb, --show-branches  Show in which branches authors have been found.\n```\n\n### Examples\n\nNormal scan, use config in home directory.\n\n```shell\n$ comiks b0oml\n```\n\nScan using another config.\n\n```shell\n$ comiks -c my_config.toml b0oml\n```\n\nIn tables output, comiks try to highlight names and emails similar to the given username. You can highlight based on other strings than the username by giving a comma-separated list of strings.\n\n```shell\n$ comiks -l john b0oml\n$ comiks -l john,doe,something b0oml\n```\n\nYou can enable/disable availables providers by updating config.toml. Now, let's imagine you have configured all the providers. But, for a given username, you only want to launch one of the providers. Rather than modifying the config each time this happens, you can select which provider to launch with tags.\n\n```shell\n$ comiks -p github,bitbucket b0oml\n$ comiks -p gitlab b0oml\n```\n\n## Providers\n\nBelow is listed all providers currently implemented.\n\n| Name      | Url                            | Authentication                                        | Enabled by default | Tags        |\n| --------- | ------------------------------ | ----------------------------------------------------- | ------------------ | ----------- |\n| GitHub    | [github.com](github.com)       | Not needed, but allows to get a higher API rate limit | yes                | `github`    |\n| GitLab    | [gitlab.com](gitlab.com)       | Needed                                                | no                 | `gitlab`    |\n| Bitbucket | [bitbucket.org](bitbucket.org) | Needed                                                | no                 | `bitbucket` |\n",
    'author': 'b0oml',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/b0oml/Comiks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
