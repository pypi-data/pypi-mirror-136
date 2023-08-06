# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mutagenesis_visualization',
 'mutagenesis_visualization.main',
 'mutagenesis_visualization.main.bar_graphs',
 'mutagenesis_visualization.main.classes',
 'mutagenesis_visualization.main.demo',
 'mutagenesis_visualization.main.heatmaps',
 'mutagenesis_visualization.main.kernel',
 'mutagenesis_visualization.main.other_stats',
 'mutagenesis_visualization.main.pca_analysis',
 'mutagenesis_visualization.main.plotly',
 'mutagenesis_visualization.main.process_data',
 'mutagenesis_visualization.main.pymol',
 'mutagenesis_visualization.main.scatter',
 'mutagenesis_visualization.main.utils',
 'mutagenesis_visualization.tests',
 'mutagenesis_visualization.tests.process_data',
 'mutagenesis_visualization.tests.utils']

package_data = \
{'': ['*'],
 'mutagenesis_visualization': ['data/*', 'data/for_tests/*', 'tutorial/*']}

install_requires = \
['XlsxWriter>=1.4.4,<2.0.0',
 'adjustText>=0.7.3,<0.8.0',
 'biopython>=1.79,<2.0',
 'dataclasses-json>=0.5.2,<0.6.0',
 'freesasa>=2.1.0,<3.0.0',
 'ipympl>=0.7.0,<0.8.0',
 'ipython>=7.31.1,<8.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.19.5,<2.0.0',
 'openpyxl>=3.0.7,<4.0.0',
 'pandas>=1.2.0,<2.0.0',
 'pillow>=9.0.0,<10.0.0',
 'plotly>=5.1.0,<6.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.5,<2.0',
 'seaborn==0.10.0',
 'statsmodels>=0.12.2,<0.13.0',
 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'mutagenesis-visualization',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'Frank',
    'author_email': 'fhidalgoruiz@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
