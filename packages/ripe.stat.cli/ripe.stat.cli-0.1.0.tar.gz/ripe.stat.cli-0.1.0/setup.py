# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cli', 'cli.tests']

package_data = \
{'': ['*'],
 'cli': ['templates/abuse-contact-finder/*',
         'templates/address-space-hierarchy/*',
         'templates/atlas-probes/spec.json',
         'templates/atlas-probes/spec.json',
         'templates/atlas-probes/template.jinja',
         'templates/atlas-probes/template.jinja',
         'templates/maxmind-geo-lite/*'],
 'cli.tests': ['data/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'argcomplete>=2.0.0,<3.0.0',
 'colorama>=0.4.4,<0.5.0',
 'requests>=2.27.1,<3.0.0',
 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['ripestat = ripe.stat.cli.command:main']}

setup_kwargs = {
    'name': 'ripe.stat.cli',
    'version': '0.1.0',
    'description': 'A CLI for RIPEStat',
    'long_description': "# The RIPEStat CLI\n\nA command line wrapper for the [RIPEStat API](https://stat.ripe.net/docs/02.data-api/atlas-probes.html).\n\n\n## How it Works\n\n```shell\nripestat maxmind-geo-lite 193.0.6.158\n193.0.6.158/32\n╒═══════════╤════════╤══════════════╤════════════╤═════════════════════════════════════════════════╕\n│ Country   │ City   │ Resources    │   Coverage │ URL                                             │\n╞═══════════╪════════╪══════════════╪════════════╪═════════════════════════════════════════════════╡\n│ NL        │        │ 193.0.0.0/20 │        100 │ https://www.google.com/maps/@52.3824,4.8995,12z │\n╘═══════════╧════════╧══════════════╧════════════╧═════════════════════════════════════════════════╛\n```\n\n\n## Installation\n\nIt's a python program, so you install it with `pip`:\n\n```shell\n$ pip install ripe.stat.cli\n```\n\nHowever, since it's a command-line tool, you might want to consider using [pipx](https://pypa.github.io/pipx/)\nto install it, as it will then be automatically added to your `${PATH}` and\npipx will handle the virtualenv shenanigans for you:\n\n```shell\n$ pipx install ripe.stat.cli\n```\n\n\n### Tab Completion\n\nOne of the nicer quirks of this tool is the tab completion.  You can do handy\nstuff like `ripestat ma<tab>` and it'll autocomplete `ripestat maxmind-geo-lite `\nfor you.  If you want to enable that, you need a few things:\n\n1. Install argcomplete.  This is a dependency of `ripestat-cli`, so it'll be\n   available in the virtualenv, but that may not be convenient.  You can always\n   install this with your operating system's package manager.  Something like\n   `apt install python-argcomplete` or `pacman -S python-argcomplete` for\n   example.\n2. Once installed, you just have to enable autocompletion as per the [official docs](https://pypi.org/project/argcomplete/#global-completion).\n   In short, this means running this on Debian-based systems:\n   ```shell\n   $ sudo activate-global-python-argcomplete\n   ```\n   or this on Arch-based systems:\n   ```shell\n   $ sudo activate-global-python-argcomplete --dest /usr/share/bash-completion/completions\n   ```\n   Alternatively, you can also install it at the user-level by dumping the\n   output of this command into a file that's sourced at login time:\n   ```shell\n   $ sudo activate-global-python-argcomplete --dest=-\n   ```\n\n## Extending\n\nThis little project doesn't yet support *all* of RIPEStat's many, *many*\nendpoints, but extending it to do so is quite easy if you're motivated:\n\n1. Create a folder under `ripe/stat/cli/templates` named for the endpoint\n   exactly as it appears in the API.  For example, the [AS Overview](https://stat.ripe.net/docs/02.data-api/as-overview.html)\n   folder would be named `as-overview` because that's what you see in the URL.\n2. In that folder create a file called: `spec.json`.  The contents of which can\n   just be copied from one of the existing folders.  The idea is to expand this\n   in the future should we want to support things like sorting or different\n   arguments etc.  For now though, it just tells the command handler that we\n   need to accept an argument called `resource`.\n3. Finally, create a Jinja template in that same folder called\n   `template.jinja`.  This template will be handed the contents of the `data`\n   portion of the API response.  You have all the powers that Jinja grants you\n   in there, so go nuts.  If you're looking for inspiration, just look at same\n   file in the other folders.\n4. Optionally, you can also add your own filters to `ripe/stat/cli/filters.py`. \n   Currently, we have `colourise()` and `as_table()` in there, but if you need\n   something special, this is where you probably want to put it.\n\n\n## TODO\n\nFor the most part, this does you'd expect -- at least for the few endpoints\ncurrently supported.  There are two glaring things that really should be done\nsoon though:\n\n1. Error handling: If the RIPEStat API barks at you with an error, this script\n   should print out a user-friendly message, maybe with some emojis and some\n   nice colour.  At the moment, it just explodes.\n2. Tests: There aren't any!  Unit tests for each filter & formatter are a bare\n   minimum, but an end-to-end test for each endpoint would be ideal.\n",
    'author': 'Daniel Quinn',
    'author_email': 'code@danielquinn.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/danielquinn/ripestat-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
