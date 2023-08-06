# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['manualindex']

package_data = \
{'': ['*'], 'manualindex': ['templates/*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0', 'fs>=2.4.14,<3.0.0']

entry_points = \
{'console_scripts': ['manualindex = manualindex.console:main']}

setup_kwargs = {
    'name': 'manualindex',
    'version': '1.0.1',
    'description': 'Generate autoindex-style HTML for your directory listings.',
    'long_description': '# manualindex\n\n[![CI](https://github.com/djmattyg007/manualindex/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/djmattyg007/manualindex/actions/workflows/ci.yml)\n[![PyPI](https://img.shields.io/pypi/v/manualindex.svg)](https://pypi.org/project/manualindex)\n\nGenerate autoindex-style HTML for your directory listings.\n\n## Install\n\n```shell\npip install manualindex\n```\n\nOr if you\'re using poetry:\n\n```shell\npoetry add manualindex\n```\n\nManualindex supports Python 3.9 and above. \n\n## Usage\n\nManualindex can be used both as a library and as a command-line program.\n\n### CLI\n\n```shell\npython -m manualindex /path/to/dir\n```\n\nA Jinja template is used to generate the `index.html` files. To customise the template, you\'ll need to pass two flags:\n\n```shell\npython -m manualindex /path/to/dir --template-path /path/to/templates --template-name mytemplate.html.j2\n```\n\nFor this example to work, there must be a file named `mytemplate.html.j2` inside `/path/to/templates`.\n\nDue to how the URL generation works, if your directory listings are not at the root of your domain, you\'ll need to pass\nthe base URL path. For example, if your base URL is `https://example.com/mydir/mysubdir/`, you will need the following:\n\n```shell\npython -m manualindex /path/to/dir --base-urlpath /mydir/mysubdir/\n```\n\nYou can customise the date format:\n\n```shell\npython -m manualindex /path/to/dir --date-format \'%Y-%m-%d\'\n```\n\nThe default date format is `%Y-%m-%d %H:%I`.\n\nTo customise the timezone of the formatted timestamps:\n\n```shell\npython -m manualindex /path/to/dir --timezone Australia/Melbourne\n```\n\nThe default timezone is UTC.\n\n### Library\n\nTo make use of all the defaults:\n\n```python\nfrom pathlib import Path\nfrom manualindex import generate_default\n\ngenerate_default(Path("/path/to/dir"))\n```\n\nTo customise the template generation options, but use the default template:\n\n```python\nfrom pathlib import Path\nfrom manualindex import default_template, generate\n\ngenerate(\n    Path("/path/to/dir"),\n    default_template,\n    base_urlpath="/mydir/mysubdir/",\n    date_format = "%Y-%m-%d",\n    date_tz="Australia/Melbourne",\n)\n```\n\nThe second parameter to `generate()` accepts any Jinja `Template` object, so you have full control over the output.\nManualindex makes no assumptions about where the template comes from.\n\n## License\n\nThe code is available under the [GPL Version 3](LICENSE.txt).\n',
    'author': 'Matthew Gamble',
    'author_email': 'git@matthewgamble.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/djmattyg007/manualindex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
