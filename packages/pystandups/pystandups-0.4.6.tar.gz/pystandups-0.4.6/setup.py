# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pystandups']

package_data = \
{'': ['*']}

install_requires = \
['coloredlogs',
 'dictdiffer',
 'docopt',
 'openeditor>=0.3.1,<0.4.0',
 'questionary',
 'tabulate']

entry_points = \
{'console_scripts': ['standup = pystandups.cli:main']}

setup_kwargs = {
    'name': 'pystandups',
    'version': '0.4.6',
    'description': 'A command line utility for working with daily standups.',
    'long_description': '# PyStandups\nA command line utility for working with daily standups. A "standup" is a brief description of what work will be done that day. PyStandups supports:\n\n* Storing standups for each day\n* Reviewing the previous day\'s standup (in case the actual work done ended up being different from what was planned)\n* A rudimentary "backlog" to save things for later standups\n\nStandups are stored as a JSON dictionary. The location is hardcoded (see `DATA_DIR`). The schema and format may change without warning between versions of PyStandups, so back this up if it\'s important. However, the goal is to keep the data simple enough to be self-explanatory and trivial to migrate.\n\n## Usage\n* `standup today` - prepare standup at the beginning of the day. PyStandups will try to intelligently fill in as much information as possible, and you will have the opportunity to edit it in your editor.\n* `standup later` - take quick notes for future standups. `standup today` automatically fills in the data from `standup later`. For more sophisticated management of planned tasks, use an external tool like Jira.\n* `standup get today` and `standup get last` - print the relevant standup to standard out. These are mainly intended for use in scripts.\n\n### Old Standups\nPyStandups does not support working with standups older than today or other complex tasks. You can use an external tool like `jq` to work with the JSON file directly.\n\n## Install\n`pip install pystandups` to install latest release.\n\nThe project is managed by [poetry](https://python-poetry.org/) so if you want to work on the code see [`poetry install`](https://python-poetry.org/docs/cli/#install).\n\nMake sure you have `$VISUAL` (preferred) or `$EDITOR` set. If relevant, the command should include the "wait" parameter so that PyStandups is blocked until you close the editor window. So for example, `subl -w` not `subl`.',
    'author': 'Azat Akhmetov',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/metov/pystandups',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
