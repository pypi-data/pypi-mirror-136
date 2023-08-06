# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['collinearity_tool']

package_data = \
{'': ['*']}

install_requires = \
['altair>=4.2.0,<5.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'patsy>=0.5.2,<0.6.0',
 'statsmodels>=0.13.1,<0.14.0']

setup_kwargs = {
    'name': 'collinearity-tool',
    'version': '0.1.6',
    'description': 'Identify multicollinearity issues by correlation, VIF, and visualizations.',
    'long_description': "# collinearity_tool\nIdentify multicollinearity issues by correlation, VIF, and visualizations. This package is designed for beginners of Python who want to identify multicollinearity issues by applying a simple function. It automates the process of building a proper correlation matrix, creating correlation heat map and identifying pairwise highly correlated variables. An R version of package is also in the progress of development.\n\n\n## 1. Description\n\n## Functions \n\nThe following four functions are in the collinearity_tool package:\n- `corr_matrix`: A function that returns a generic correlation matrix and a longer form one for all numerical variables in a data frame.\n- `corr_heatmap`: A function that returns a correlation heatmap given a dataframe.\n- `vif_bar_plot`: A function that returns a list containing a data frame for Variable Inflation Factors (VIF) and a bar chart of the VIFs for each explanatory variable in a multiple linear regression model.\n- `col_identify`: A function that identifies multicollinearity based on highly correlated pairs (using Pearson coefficient) with VIF values exceeding the threshold.\n\n## Package ecosystems\n\n**Motivation** \nThis package aims to fill the simplify the decision-making process while addressing multicollinearity. This tool brings several other packages together into one interface.\nMulticollinearity tools exist but they do not encompass all of the components included in this tool.\n\nFor example, linear regression, plotting tools and correlation matrix packages are already part of the Python ecosystem (as part of Pandas, Scipy, and so on).\nWhat makes this package different is that it combines the tools together to create a single package that will allow the researcher to locate troublesome multicollinearity issues.\n\nIn addition, the collinearity_tool helps new users, unfamiliar with Python and its broad ecosystem, to plot and deduce multicollinearity without prior knowledge of plotting, calculating VIFF's or manipulating data to create plots and tables.\n\n`variance_inflation_factor()`\nThis function is necessary to calculate VIF. It is part of the _statsmodels_ [documentation](https://www.statsmodels.org/dev/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html) package. The VIF package calculates the VIF score which predicts how well the variable can be predicted using other explanatory variables in the dataset using linear regression. Higher values highlight multicollinearity problems.\nThe output is a simple dataframe with two columns: feature (variable name) and VIF (VIF value).\n\n`scipy.stats.linregress`  \nScipy is a necessary package for this collinearity tool. This package conducts linear regression using `linregress` and provides necessary statistical information. For more information on the package, please see the following [documentation](https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.stats.linregress.html).\n\n**Pandas**: `corr()`    \nPandas is another necessary package for this collinearity tool. This package conducts linear regression using and produces a correlation matrix using `corr`. The output is a DataFrame in the shape of a correlation matrix.\nFor more information on the package, please see the following [documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.corr.html)).\n\n**Altair**  \n_Altair_ is a popular plotting package. It provides the necessary tools to create the heatmap for the collinearity tool. For more information on Altair and heatmaps, please refer to this [example](https://altair-viz.github.io/gallery/simple_heatmap.html).\n\n## 2. Installation\n\n```bash\n$ pip install git+https://github.com/UBC-MDS/collinearity_tool.git\n```\n\n## 3. Usage\n\n`collinearity` can be used to  identify multicollinearity issues by correlation, VIF, and visualizations as follows:\n\n```python\nimport pandas as pd\nimport collinearity_tool.collinearity_tool as cl\n\ndata = pd.read_csv('test.csv') # path to your file\ncl.corr_matrix(data)\ncl.corr_heatmap(data)\nvif = cl.vif_bar_plot(x, y, data, 6) # x and y are the choice of the variables\ncl.col_identify(data, x, y)\n```\n\n## 4. Contributors\n- Anahita Einolghozati\n- Chaoran Wang\n- Katia Aristova\n- Lisheng Mao\n\n## 5. Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## 6. License\n\n`collinearity_tool` was created by Anahita Einolghozati, Chaoran Wang, Katia Aristova, Lisheng Mao. It is licensed under the terms of the MIT license.\n\n## 7. Credits\n\n`collinearity_tool` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n",
    'author': 'Anahita Einolghozati, Chaoran Wang, Katia Aristova, Lisheng Mao',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UBC-MDS/collinearity_tool',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
