[![ci-cd](https://github.com/UBC-MDS/features_creator/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/features_creator/actions/workflows/ci-cd.yml)
[![Documentation Status](https://readthedocs.org/projects/features_creator/badge/?version=latest)](https://features_creator.readthedocs.io/en/latest/?badge=latest)
# features_creator

Helper functions to create new features for temporal data.

## Contributors

- Nikita Shymberg
- Rakesh Pandey
- Son Chau
- Wenjia Zhu

## Description

This package aims to speed up and simplify the process of feature engineering for temporal (e.g. weekly or monthly) data.
It works with dataframes that have columns whose names follow a pattern and end with a number. For example payment_week_1, payment_week_2, ...
For such datasets, commonly engineered features include, among others, the percentage change across time periods, the average across time periods, and the standard deviation across time periods.

This package defines the following four functions:

- `get_matching_column_names`: Returns a subset of the columns whose names match the pattern. This is a prerequisite for the feature engineering
- `calculate_average`: Returns the average value across matching columns for each row.
- `calculate_standard_deviation`: Returns the stadard deviation across matching columns for each row.
- `calculate_percentage_change`: Returns the percent change across consecutive time periods for each row.

### How does this package fit into the existing ecosystem?

There are many Python libraries available that facilitate feature engineering,
the two most common ones are [Featuretools](https://www.featuretools.com/) and [Feature-engine](https://feature-engine.readthedocs.io/en/1.2.x/).
`Featuretools` has much more functionality than `features_creator`, but is more heavyweight and comes with a steeper learning curve.
It also requires quite a lot of data massaging to get it into the correct format before features can be engineered.
`Feature-engine` also has a wide variety of functionality, but it is not tailored to temporal data.
`Feature-engine` is more focused on data imputation, discretization, encoding, and outlier removal.

For datasets that have columns that follow the pattern `quantity_1`, `quantity_2`, ... `features_creator` is the simplest package for engineering features.

## Installation

```bash
$ pip install features_creator
```

## Usage

```python
import pandas as pd
from IPython.display import display
from features_creator.features_creator import (
    get_matching_column_names,
    calculate_standard_deviation,
    calculate_average,
    calculate_percentage_change,
)

# Example data
df = pd.DataFrame(
    {
        "subscriber_id": [1, 2, 3],
        "data_usage1": [10, 5, 3],  # 1 represent data usage in prediction month (m) - 1
        "data_usage2": [4, 5, 6],  # m - 2
        "data_usage3": [7, 8, 9],  # m - 3
        "data_usage4": [10, 11, 12],  # m - 4
        "data_usage5": [13, 14, 15],  # m - 5
        "othercolumn": [5, 6, 7],  # Other example column
        "data_usage_string6": [5, 6, 7],  # Other example column with an integer
    }
)

# Get matching column names
columns = get_matching_column_names(df, "data_usage")

# Calculate standard deviation across time periods
df["std_monthly_data_usage"] = calculate_standard_deviation(df, "data_usage")

# Calculate average across time periods
df["avg_monthly_data_usage"] = calculate_average(df, "data_usage")

# Calculate percentage change 2 months over 2 months
df["percent_change_data_usage"] = calculate_percentage_change(
    df, "data_usage", compare_period=(2, 2)
)

# Display data
display(
    df[[
        "subscriber_id",
        "std_monthly_data_usage",
        "avg_monthly_data_usage",
        "percent_change_data_usage",
    ]]
)
   subscriber_id  std_monthly_data_usage  avg_monthly_data_usage  percent_change_data_usage
0              1                3.059412                     8.8                 -17.647059
1              2                3.498571                     8.6                 -47.368421
2              3                4.242641                     9.0                 -57.142857
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`features_creator` was created by DSCI_524_GROUP26. It is licensed under the terms of the MIT license.

## Credits

`features_creator` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
