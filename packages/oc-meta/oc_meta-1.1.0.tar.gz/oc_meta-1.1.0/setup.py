# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oc_meta',
 'oc_meta.lib',
 'oc_meta.lib.id_manager',
 'oc_meta.plugins',
 'oc_meta.plugins.crossref',
 'oc_meta.plugins.csv_generator',
 'oc_meta.plugins.multiprocess',
 'oc_meta.plugins.orcid',
 'oc_meta.run',
 'oc_meta.scripts']

package_data = \
{'': ['*']}

install_requires = \
['Pebble>=4.6.3,<5.0.0',
 'PyYAML>=6.0,<7.0',
 'SPARQLWrapper==1.8.5',
 'argparse>=1.4.0,<2.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'filelock>=3.6.0,<4.0.0',
 'lxml>=4.8.0,<5.0.0',
 'oc-ocdm>=7.0.0,<8.0.0',
 'psutil>=5.9.0,<6.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'rdflib>=6.1.1,<7.0.0',
 'requests>=2.27.1,<3.0.0',
 'time-agnostic-library>=3.1.0,<4.0.0',
 'tqdm>=4.64.0,<5.0.0']

entry_points = \
{'console_scripts': ['test = test.run_all_tests:main']}

setup_kwargs = {
    'name': 'oc-meta',
    'version': '1.1.0',
    'description': 'OpenCitations Meta contains bibliographic metadata associated with the documents involved in the citations stored in the OpenCitations infrastructure. The OpenCitations Meta Software performs two main actions: a data curation of the provided CSV files and the generation of new RDF files compliant with the OpenCitations Data Model.',
    'long_description': None,
    'author': 'Arcangelo Massari',
    'author_email': 'arcangelomas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
