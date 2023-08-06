# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['canadacovidmetrics']

package_data = \
{'': ['*']}

install_requires = \
['DateTime>=4.3,<5.0',
 'pandas>=1.3.5,<2.0.0',
 'pytest>=6.2.5,<7.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'canadacovidmetrics',
    'version': '0.1.0',
    'description': 'This package enables obtain key metrics regarding covid situation in Canada',
    'long_description': '# canadacovidmetrics\n\nThis is a Python package that provides key metrics regarding COVID-19 situation in Canada across provinces using the [OpenCovid API](https://opencovid.ca/api/).\n\n## Summary\n\nThis package allows users to obtain key metrics on COVID-19 situation in Canada at national or provincial level for a specific time period. The 4 functions will return key metrics, including total cumulative cases, total cumulative deaths, total cumulative recovered cases and total cumulative vaccine completion, using data from [OpenCovid API](https://opencovid.ca/api/). The users may use the key metrics to conduct further analyses on COVID-19 situation in Canada.\n\n## Functions\n\nThere are 4 functions in this package:\n\n-   `total_cumulative_cases` Query total cumulative cases with ability to specify province and date range of returned data.\n\n-   `total_cumulative_deaths` Query total cumulative deaths with ability to specify province and date range of returned data.\n\n-   `total_cumulative_recovered_cases` Query total cumulative recovered cases with ability to specify province and date range of returned data.\n\n-   `total_cumulative_vaccine_completion` Query total cumulative vaccine completion with ability to specify province and date range of returned data.\n\n## Installation\n\n```bash\n$ pip install "git+https://github.com/UBC-MDS/canadacovidmetrics"\n```\n\n## Usage\n\n- TODO\n\n## Python ecosystem\n\nThere are several packages for easy access to COVID-19 key metrics or data using different APIs, examples include\n- [covid](https://github.com/nf1s/covid) using [John Hopkins University API](https://coronavirus.jhu.edu/about/)\n- [COVID19Py](https://github.com/Kamaropoulos/COVID19Py) using [Coronavirus Tracker API](https://github.com/ExpDev07/coronavirus-tracker-api)\n- [covid19pyclient](https://github.com/NiklasTiede/covid19pyclient) using [RKI API](https://github.com/marlon360/rki-covid-api)\n\nTo our knowledge, there is no similar package using [OpenCovid API](https://opencovid.ca/api/) in the Python ecosystem.\n\n## Contributors\n\n-   Adam Morphy (@adammorphy)\n-   Brandon Lam (@ming0701)\n-   Lakshmi Santosha Valli Akella (@valli180)\n-   Luke Collins (@LukeAC)\n\nWe welcome and recognize all contributions. Please find the guide for contribution in [Contributing Document](https://github.com/UBC-MDS/canadacovidmetrics/blob/main/CONTRIBUTING.md).\n\n## License\n\n`canadacovidmetrics` was created by the Contributors. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`canadacovidmetrics` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Valli A',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
