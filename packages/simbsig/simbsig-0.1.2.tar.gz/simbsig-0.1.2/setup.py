# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['simbsig',
 'simbsig.base',
 'simbsig.cluster',
 'simbsig.decomposition',
 'simbsig.neighbors',
 'simbsig.utils']

package_data = \
{'': ['*']}

install_requires = \
['h5py>=3.7.0,<4.0.0',
 'numpy>=1.22.0,<2.0.0',
 'scikit-learn>=1.1.0,<2.0.0',
 'torch>=1.9.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'simbsig',
    'version': '0.1.2',
    'description': 'A python package for out-of-core similarity search and dimensionality reduction',
    'long_description': "# SIMBSIG = SIMilarity Batched Search Integrated Gpu-based\n\n\n[![License: BSD](https://img.shields.io/github/license/BorgwardtLab/simbsig)](https://opensource.org/licenses/BSD-3-Clause)\n[![Version](https://img.shields.io/pypi/v/simbsig)](https://pypi.org/project/simbsig/)\n[![PythonVersion](https://img.shields.io/pypi/pyversions/simbsig)]()\n[![Documentation Status](https://readthedocs.org/projects/simbsig/badge/?version=latest)](https://simbsig.readthedocs.io/en/latest/?badge=latest)\n\nSIMBSIG is a GPU accelerated software tool for neighborhood queries, KMeans and PCA which mimics the sklearn API.\n\nThe algorithm for batchwise data loading and GPU usage follows the principle of [1]. The algorithm for KMeans follows the Mini-batch KMeans described by Scully [2]. The PCA algorithm follows Halko's method [3].\nThe API matches sklearn in big parts [4,5], such that code dedicated to sklearn can be simply reused by importing SIMBSIG instead of sklearn. Additional features and arguments for scaling have been added, for example all data input can be either array-like or as a h5py file handle [6].\n\n*Eljas Röllin, Michael Adamer, Lucie Bourguignon, Karsten M. Borgwardt*\n\n\n## Installation\n\nSIMBSIG is a PyPI package which can be installed via `pip`:\n\n```\npip install simbsig\n```\n\nYou can also clone the repository and install it locally via [Poetry](https://python-poetry.org/) by executing\n```bash\npoetry install\n```\nin the repository directory.\n\n## Example\n\n<!-- Python block-->\n```python\n>>> X = [[0,1], [1,2], [2,3], [3,4]]\n>>> y = [0, 0, 1, 1]\n>>> from simbsig import KNeighborsClassifier\n>>> knn_classifier = KNeighborsClassifier(n_neighbors=3)\n>>> knn_classifier.fit(X, y)\nKNeighborsClassifier(...)\n>>> print(knn_classifier.predict([[0.9, 1.9]]))\n[0]\n>>> print(knn_classifier.predict_proba([[0.9]]))\n[[0.666... 0.333...]]\n```\n\n## Tutorials\nTutorial notebooks with toy examples can be found under [tutorials](https://github.com/BorgwardtLab/simbsig/tree/main/tutorials)\n\n## Documentation\n\nThe documentation can be found [here](https://simbsig.readthedocs.io/en/latest/index.html).\n\n## Overview of implemented algorithms\n\n| Class | SIMBSIG | sklearn |\n| :---: | :--- | :--- |\n| NearestNeighbors | fit | fit |\n|  | kneighbors | kneighbors |\n|  | radius_neighbors | radius_neighbors |\n| KNeighborsClassifier | fit | fit |\n|  | predict | predict |\n|  | predict_proba | predict_proba |\n| KNeighborsRegressor | fit | fit |\n|  | predict | predict |\n| RadiusNeighborsClassifier | fit | fit |\n|  | predict | predict |\n|  | predict_proba | predict_proba |\n| RadiusNeighborsRegressor | fit | fit |\n|  | predict | predict |\n| KMeans |  fit | fit|\n| | predict | predict |\n| | fit_predict | fit_predict |\n| PCA | fit | fit |\n|  | transform | transform |\n|  | fit_transform | fit_transform\n\n## Contact\n\nThis code is developed and maintained by members of the Department of Biosystems Science and Engineering at ETH Zurich. It available from the GitHub repo of the [Machine Learning and Computational Biology Lab](https://www.bsse.ethz.ch/mlcb) of [Prof. Dr. Karsten Borgwardt](https://www.bsse.ethz.ch/mlcb/karsten.html).\n\n- [Michael Adamer](https://mikeadamer.github.io/) ([GitHub](https://github.com/MikeAdamer))\n\n*References*:\n\n  [1] Gutiérrez, P. D., Lastra, M., Bacardit, J., Benítez, J. M., & Herrera, F. (2016). GPU-SME-kNN: Scalable and memory efficient kNN and lazy learning using GPUs. Information Sciences, 373, 165-182.\n\n  [2] Sculley, D. (2010, April). Web-scale k-means clustering. In Proceedings of the 19th international conference on World wide web (pp. 1177-1178).\n\n  [3] Halko, N., Martinsson, P. G., Shkolnisky, Y., & Tygert, M. (2011). An algorithm for the principal component analysis of large data sets. SIAM Journal on Scientific computing, 33(5), 2580-2594.\n\n  [4] Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., ... & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. the Journal of machine Learning research, 12, 2825-2830.\n\n  [5] Buitinck, L., Louppe, G., Blondel, M., Pedregosa, F., Mueller, A., Grisel, O., ... & Varoquaux, G. (2013). API design for machine learning software: experiences from the scikit-learn project. arXiv preprint arXiv:1309.0238.\n\n  [6] Collette, A., Kluyver, T., Caswell, T. A., Tocknell, J., Kieffer, J., Scopatz, A., ... & Hole, L. (2021). h5py/h5py: 3.1. 0. Zenodo.\n",
    'author': 'Eljas Roellin',
    'author_email': 'roelline@student.ethz.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/BorgwardtLab/simbsig',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
