# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bento',
 'bento.datasets',
 'bento.io',
 'bento.plotting',
 'bento.preprocessing',
 'bento.tools']

package_data = \
{'': ['*'], 'bento': ['models/*']}

install_requires = \
['Shapely>=1.8.2,<2.0.0',
 'UpSetPlot>=0.6.1,<0.7.0',
 'anndata>=0.7.6,<0.8.0',
 'astropy>=5.0,<6.0',
 'cell2cell>=0.5.10,<0.6.0',
 'dask-geopandas>=0.1.3,<0.2.0',
 'emoji>=1.7.0,<2.0.0',
 'geopandas>=0.10.0,<0.11.0',
 'matplotlib-scalebar>=0.8.1,<0.9.0',
 'matplotlib>=3.2,<4.0',
 'numba>=0.55.2,<0.56.0',
 'pandas<=1.2.5',
 'pygeos>=0.12.0,<0.13.0',
 'scanpy>=1.9.1,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'seaborn>=0.11.0,<0.12.0',
 'statsmodels>=0.13.2,<0.14.0',
 'tqdm>=4.64.0,<5.0.0',
 'xgboost==1.4.0']

extras_require = \
{'docs': ['myst-parser>=0.18.0,<0.19.0',
          'nbsphinx>=0.8.9,<0.9.0',
          'Sphinx>=4.1.2,<5.0.0',
          'sphinx-autobuild>=2021.3.14,<2022.0.0',
          'sphinx-book-theme>=0.3.2,<0.4.0',
          'sphinx-gallery>=0.10.1,<0.11.0'],
 'torch': ['torch>=1.9.0,<2.0.0']}

setup_kwargs = {
    'name': 'bento-tools',
    'version': '1.0.1',
    'description': 'A toolkit for subcellular analysis of spatial transcriptomics data',
    'long_description': '[![PyPI version](https://badge.fury.io/py/bento-tools.svg)](https://badge.fury.io/py/bento-tools)\n[![codecov](https://codecov.io/gh/ckmah/bento-tools/branch/master/graph/badge.svg?token=XVHDKNDCDT)](https://codecov.io/gh/ckmah/bento-tools)\n[![Documentation Status](https://readthedocs.org/projects/bento-tools/badge/?version=latest)](https://bento-tools.readthedocs.io/en/latest/?badge=latest)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/bento-tools)\n[![GitHub stars](https://badgen.net/github/stars/ckmah/bento-tools)](https://GitHub.com/Naereen/ckmah/bento-tools) \n\n\n<img src="docs/source/_static/bento-name.png" alt="Bento Logo" width=350>\n\nBento is a Python toolkit for performing subcellular analysis of spatial transcriptomics data.\n\n# Get started\nInstall with Python 3.8 or 3.9:\n```bash\npip install bento-tools\n```\n\nCheck out the [documentation](https://bento-tools.readthedocs.io/en/latest/) for the installation guide, tutorials, API and more! Read and cite [our preprint](https://doi.org/10.1101/2022.06.10.495510) if you use Bento in your work.\n\n\n# Main Features\n\n<img src="docs/source/_static/tutorial_img/bento_workflow.png" alt="Bento Analysis Workflow" width=800>\n\n\n- Store molecular coordinates and segmentation masks\n- Visualize spatial transcriptomics data at subcellular resolution\n- Compute subcellular spatial features\n- Predict localization patterns and signatures\n- Factor decomposition for high-dimensional spatial feature sets\n\n---\n[![GitHub license](https://img.shields.io/github/license/ckmah/bento-tools.svg)](https://github.com/ckmah/bento-tools/blob/master/LICENSE)\n',
    'author': 'Clarence Mah',
    'author_email': 'ckmah@ucsd.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
