# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['strapvizpy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'strapvizpy',
    'version': '0.1.0',
    'description': 'Performs bootstrapping of a dataset to produce plots and statistics for use in final reports and documents. ',
    'long_description': "# strapvizpy\n\n## Summary\n\nPerforms bootstrapping of a dataset column to produce plots and statistics for use in final reports and documents.\n\nThe purpose of this package is to simplify and automate the process of creating simple bootstrap distributions of numerical data columns. The package will have a module which intakes a dataset column and relevant parameters such as the desired confidence bounds and number of simulations. The module will perform the simulation statistics to generate the bootstrap mean distribution and relevant statistics such as the sample mean and bootstrapped confidence interval. The package will also contain a module for visualization of the bootstraped confidence interval, and a module for creating a professional publication-ready table of the relevant statistics.\n\n## Package context within the Python ecosystem\n\nThe package will likely build on scipy's [stats module](https://docs.scipy.org/doc/scipy/reference/stats.html), which allows one to conduct the boostrap sampling in the first place using the bootstrap method. strapvizpy will streamline and extend this process from the pure statistical process done in this module. sklearn has a utils module with a [resample](https://scikit-learn.org/stable/modules/generated/sklearn.utils.resample.html) method which also seems popular and achieves similar functionality. While we cannot be certain that one does not exist, there does not seem to be a package which streamlines the process from data to visualization and presentation as proposed in this document. Some tutorials on bootstrap confidence intervals from [machinelearningmastery.com](https://machinelearningmastery.com/calculate-bootstrap-confidence-intervals-machine-learning-results-python/) and [towardsdatascience.com](https://towardsdatascience.com/bootstrapping-using-python-and-r-b112bb4a969e) encourage the reader to plot the results manually.\n\n\n## Installation\n\n```bash\n$ pip install -i https://test.pypi.org/simple/ strapvizpy\n```\n\n## Function Usage\n\n- **bootstrap_distribution:** A sampling distribution of `rep` replicates is generated for a specified estimator with replacement for a given bootstrap sample size.  \n- **calculate_boot_stats:** Calculates a confidence interval for a given sampling distribution as well as other bootstapped statistics.  \n- **histogram_ci_plot:** Makes a histogram of a boostrapped sampling distribution with its confidence interval and oberserved sample statistic.  \n- **summary_tabels:** Generates a table that contains a given sampling distribution's mean and standard deviation along with relevant statistics as well as a summary table of the bootstrap distributions parameters  \n\n## Contributing\nJulien Gordon, Gautham Pughazhendhi, Zack Tang, and Margot Vore.\n\n## License\n\n`strapvizpy` was created by Julien Gordon, Gautham Pughazhendhi, Zack Tang, Margot Vore. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`strapvizpy` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n",
    'author': 'Julien Gordon, Gautham Pughazhendhi, Zack Tang, Margot Vore',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
