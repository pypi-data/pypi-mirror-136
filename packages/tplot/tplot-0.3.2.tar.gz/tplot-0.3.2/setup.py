# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tplot']

package_data = \
{'': ['*']}

install_requires = \
['backports.cached-property>=1.0.1,<2.0.0',
 'colorama>=0.4.3,<0.5.0',
 'numpy>=1.11,<2.0',
 'termcolor-whl>=1.1.0,<2.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3.1.0,<4.0.0']}

setup_kwargs = {
    'name': 'tplot',
    'version': '0.3.2',
    'description': 'Create text-based graphs',
    'long_description': '# tplot\n\n[![Documentation status](https://readthedocs.org/projects/tplot/badge/)](https://tplot.readthedocs.io/en/latest/)\n[![Tests status](https://github.com/JeroenDelcour/tplot/actions/workflows/tests.yml/badge.svg)](https://github.com/JeroenDelcour/tplot/actions/workflows/tests.yml)\n[![codecov](https://codecov.io/gh/JeroenDelcour/tplot/branch/master/graph/badge.svg?token=WXH7I3BGEO)](https://codecov.io/gh/JeroenDelcour/tplot)\n\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/tplot)](https://pypi.org/project/tplot/)\n[![PyPI version](https://img.shields.io/pypi/v/tplot)](https://pypi.org/project/tplot/)\n[![License](https://img.shields.io/github/license/jeroendelcour/tplot)](https://github.com/JeroenDelcour/tplot/blob/master/LICENSE)\n\n`tplot` is a Python package for creating text-based graphs. Useful for visualizing data to the terminal or log files.\n\n## Features\n\n- Scatter plots, line plots, horizontal/vertical bar plots, and image plots\n- Supports numerical and categorical data\n- Legend\n- Unicode characters (with automatic ascii fallback)\n- Colors\n- Few dependencies\n- Fast and lightweight\n- Doesn\'t take over your terminal (only prints strings)\n\n## Installation\n\n`tplot` is available on [PyPi](https://pypi.org/project/tplot/):\n\n```bash\npip install tplot\n```\n\n## Documentation\n\nDocumentation is available on [readthedocs](https://tplot.readthedocs.io/en/latest/).\n\n## Examples\n\n### Basic usage\n\n```python\nimport tplot\n\nfig = tplot.Figure()\nfig.scatter([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])\nfig.show()\n```\n\n![Basic example](docs/images/basic.png)\n\n### A more advanced example\n\n```python\nimport tplot\nimport numpy as np\n\nx = np.linspace(start=0, stop=np.pi*3, num=80)\n\nfig = tplot.Figure(\n    xlabel="Phase",\n    ylabel="Amplitude",\n    title="Trigonometric functions",\n    legendloc="bottomleft",\n    width=60,\n    height=15,\n)\nfig.line(x, y=np.sin(x), color="red", label="sin(x)")\nfig.line(x, y=np.cos(x), color="blue", label="cos(x)")\nfig.show()\n```\n\n![Advanced example](docs/images/advanced.png)\n\nSee more examples in the [documentation](https://tplot.readthedocs.io/en/latest/).\n\n## Contributing\n\nContributions are welcome. Bug fixes, feature suggestions, documentation improvements etc. can be contributed via [issues](https://github.com/JeroenDelcour/tplot/issues) and/or [pull requests](https://github.com/JeroenDelcour/tplot/pulls).\n',
    'author': 'Jeroen Delcour',
    'author_email': 'jeroendelcour@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JeroenDelcour/tplot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
