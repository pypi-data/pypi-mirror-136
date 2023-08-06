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
$ pip install git+https://github.com/UBC-MDS/features_creator
```

## Usage

- TODO

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`features_creator` was created by DSCI_524_GROUP26. It is licensed under the terms of the MIT license.

## Credits

`features_creator` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
