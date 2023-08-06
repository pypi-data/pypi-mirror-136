# canadacovidmetrics

This is a Python package that provides key metrics regarding COVID-19 situation in Canada across provinces using the [OpenCovid API](https://opencovid.ca/api/).

## Summary

This package allows users to obtain key metrics on COVID-19 situation in Canada at national or provincial level for a specific time period. The 4 functions will return key metrics, including total cumulative cases, total cumulative deaths, total cumulative recovered cases and total cumulative vaccine completion, using data from [OpenCovid API](https://opencovid.ca/api/). The users may use the key metrics to conduct further analyses on COVID-19 situation in Canada.

## Functions

There are 4 functions in this package:

-   `total_cumulative_cases` Query total cumulative cases with ability to specify province and date range of returned data.

-   `total_cumulative_deaths` Query total cumulative deaths with ability to specify province and date range of returned data.

-   `total_cumulative_recovered_cases` Query total cumulative recovered cases with ability to specify province and date range of returned data.

-   `total_cumulative_vaccine_completion` Query total cumulative vaccine completion with ability to specify province and date range of returned data.

## Installation

```bash
$ pip install "git+https://github.com/UBC-MDS/canadacovidmetrics"
```

## Usage

- TODO

## Python ecosystem

There are several packages for easy access to COVID-19 key metrics or data using different APIs, examples include
- [covid](https://github.com/nf1s/covid) using [John Hopkins University API](https://coronavirus.jhu.edu/about/)
- [COVID19Py](https://github.com/Kamaropoulos/COVID19Py) using [Coronavirus Tracker API](https://github.com/ExpDev07/coronavirus-tracker-api)
- [covid19pyclient](https://github.com/NiklasTiede/covid19pyclient) using [RKI API](https://github.com/marlon360/rki-covid-api)

To our knowledge, there is no similar package using [OpenCovid API](https://opencovid.ca/api/) in the Python ecosystem.

## Contributors

-   Adam Morphy (@adammorphy)
-   Brandon Lam (@ming0701)
-   Lakshmi Santosha Valli Akella (@valli180)
-   Luke Collins (@LukeAC)

We welcome and recognize all contributions. Please find the guide for contribution in [Contributing Document](https://github.com/UBC-MDS/canadacovidmetrics/blob/main/CONTRIBUTING.md).

## License

`canadacovidmetrics` was created by the Contributors. It is licensed under the terms of the MIT license.

## Credits

`canadacovidmetrics` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
