# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dsimplex']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.4,<2.0.0', 'scipy>=1.8.1,<2.0.0']

entry_points = \
{'console_scripts': ['dsimplex = dsimplex.simplex:dsimplex']}

setup_kwargs = {
    'name': 'dsimplex',
    'version': '0.1.10',
    'description': '',
    'long_description': '[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5fd619053adf4ce88c4333e306aafa4a)](https://www.codacy.com/gh/terminaldweller/simplex/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=terminaldweller/simplex&amp;utm_campaign=Badge_Grade)\n[![Total alerts](https://img.shields.io/lgtm/alerts/g/terminaldweller/simplex.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/terminaldweller/simplex/alerts/)\n\n# Simplex\n\nA python package that solve linear programming problems using the simplex method.<br/>\nFeatures:<br/>\n* The Problem is input into the program by a file containing python expression.<br/>\n* Solves both min and max problems(duh!).<br/>\n* Uses the big M method to find a basic feasible solution when there are none available in the original program.<br/>\n* Handles adding slack variables to convert the problem into standard form.<br/>\n* Uses the lexicographic rule to prevent ending up in a loop due to degenerate extreme points.<br/>\n\nRun Help to get a list of available commandline options.<br/>\n```sh\nusage: simplex.py [-h] [--equs EQUS] [--slack SLACK] [--aux AUX] [--iter ITER]\n                  [--min] [--verbose] [--debug] [--numba]\n\noptions:\n  -h, --help            show this help message and exit\n  --equs EQUS, -e EQUS  the file containing the equations\n  --slack SLACK, -s SLACK\n                        slack variable base name, names are cretedby adding a\n                        number to the string\n  --aux AUX, -a AUX     aux variable base name, names are cretedby adding a\n                        number to the string\n  --iter ITER, -i ITER  maximum number of iterations\n  --min, -m             determines whether its a minimization problem.if not,\n                        its a maximization problem\n  --verbose, -v         whether to print output verbosely\n  --debug, -d           whether to print debug info\n```\nExample usage:<br/>\n```sh\n./simplex.py -e ./tests/equ6.py -a xa -v -s z -m\n```\n\n## TODO\n* Use numba\n',
    'author': 'terminaldweller',
    'author_email': 'thabogre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/terminaldweller/simplex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
