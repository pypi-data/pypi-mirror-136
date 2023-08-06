# pyeasyeda

[![ci-cd](https://github.com/UBC-MDS/pyeasyeda/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/pyeasyeda/actions/workflows/ci-cd.yml) [![codecov](https://codecov.io/gh/UBC-MDS/pyeasyeda/branch/main/graph/badge.svg?token=vaOyqFqkor)](https://codecov.io/gh/UBC-MDS/pyeasyeda)

Since exploratory data analysis is an imperative part of every analysis, this package aims at providing efficient data scrubbing and visualization tools to perform preliminary EDA on raw data. The package can be leveraged to clean the dataset and visualize relationships between features to generate insightful trends.

## Functions

-   `clean_up` - This function takes in a pandas dataframe object and performs initial steps of EDA on unstructured data. It returns a clean dataset by removing null values and identifying potential outliers in numeric variables based on a defined threshold.

-   `birds_eye_view` - This function takes in a pandas dataframe object and visualizes the distributions of variables in the form of histograms and density plots. It also generates a correlation heatmap for numeric variables to study their relationships.

-   `close_up` - This function accepts a pandas dataframe object creates a scatterplot of the variable(s) most strongly correlated with the dependent variable. The plot also produces a trend line to model the correlation between the variables.

-   `summary_suggestions` - This function takes in a pandas dataframe object and outputs a table of summary statistics for numeric and categorical variables and a table for percentage of unique values in the categorical variables.

Other packages that offer similar functionality are:
- [datascience_eda](https://github.com/UBC-MDS/datascience_eda)
- [QuickDA](https://github.com/sid-the-coder/QuickDA)
- [easy-data-analysis](https://github.com/jschnab/easy-data-analysis)

## Installation

```bash
$ pip install pyeasyeda
```

## Usage
Please refer to the documentation link provided below, under 'Example usage' section, for the detailed demonstration of how to use the package.

## Documentation
The official documentation is hosted on Read the Docs: https://pyeasyeda.readthedocs.io/en/latest/

## Contributors
This python package was developed by James Kim, Kristin Bunyan, Luming Yang and Sukhleen Kaur. The team is from the Master of Data Science program at the University of the British Columbia.

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`pyeasyeda` was created by James Kim, Kristin Banyan, Luming Yang and Sukhleen Kaur. It is licensed under the terms of the MIT license.

## Credits

`pyeasyeda` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
