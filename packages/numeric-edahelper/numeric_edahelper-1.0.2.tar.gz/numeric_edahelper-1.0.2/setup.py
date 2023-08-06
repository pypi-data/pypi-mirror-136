# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['numeric_edahelper']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.1,<2.0.0', 'pandas>=1.3.5,<2.0.0']

setup_kwargs = {
    'name': 'numeric-edahelper',
    'version': '1.0.2',
    'description': 'Exploratory data analysis package for data that is numeric in nature.',
    'long_description': '\n# numeric_edahelper\n\nData scientists often spend alot of time preprocessing data to extract useful parts for their analysis. The numeric_edahelper package is a package that aims to streamline Exploratory Data Analysis, specifically for numeric data in datasets. The goal is to simplify some common and repetitive tasks during EDA and data preprocessing for data analysts, as well as add value to their workflow by presenting some useful insights in a quick manner (just calling our functions), such as displaying highly-correlated variables and outliers. \n\nThe package includes functions which can complete the following tasks:\n\n- Display some useful statistics\n- Detect outliers\n- Deal with missing values\n- Check for correlation between features\n\n## Usage\n\nIn your Python interpreter, follow the example below:\n```\nimport pandas as pd\nimport numpy as np\nfrom numeric_edahelper.overview import overview\nfrom numeric_edahelper.flag_outliers import flag_outliers\nfrom numeric_edahelper.missing_imputer import missing_imputer\nfrom numeric_edahelper.get_correlated_features import get_correlated_features\ndf = pd.DataFrame({\'col1\': [-100,-200, 1,2,3,4,5,6,7,8,9,np.nan, 1000], \n                   \'col2\': [1,2,3,4,5,6,7,8,9,10,11,12,13],\n                   \'col3\': [-50, 1,2,3,4,5,6,7,8,9,10,11,50000]})\noverview(df, quiet=False)\nmissing_imputer(df, method="median")\nflag_outliers(df, threshold=0.2)\nget_correlated_features(df, threshold=0.7)\n```\n\n## Function descriptions\n\n- `overview`: This function calculates common descriptive statistical values of in the input data. Users can choose the extent of information that is returned and have the option to use the function as a means to create statistical variables to be used elsewhere in the environment.\n- `flag_outliers`: This function helps to display numeric variables which contain outliers that exceed a certain user-specified threshold percentage, using the interquartile range method. Users can then take note of these variables with high percentage of outliers and decide what to do with the variable(s).\n- `missing_imputer`:This function aims to detect missing values in the numeric data frame and using strategies including drop, mean or median to drop missing values or to replace them with the mean or median of other values in the same column.\n- `get_correlated_features`:This function will get pairs of features which have correlation above a threshold value. We can specify if we want to check only the magniture of correlation value or we also want to consider sign (positive/ negative).\n\n## Similar Work\n\nIn the Python open-source ecosystem, there exists some useful packages that already  tackle EDA and preprocessing, but our goal is to make it even more light-weighted, fast and specifically tailored to present numeric EDA insights. One popular and useful package that can generate EDA reports is: \n\n- [`pandasprofiling`](https://github.com/pandas-profiling/pandas-profiling)\n\n\n## Contributors\n\nWe welcome all contributions and the current main contributors are:\n\n-   Anupriya Srivastava \n-   Jiwei Hu \n-   Michelle Wang \n-   Samuel Quist\n\n\n## License\n\nLicensed under the terms of the MIT license.\n\n## Credits\n\n`numeric_edahelper` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n\n',
    'author': 'Samuel Quist',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UBC-MDS/numeric_edahelper',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
