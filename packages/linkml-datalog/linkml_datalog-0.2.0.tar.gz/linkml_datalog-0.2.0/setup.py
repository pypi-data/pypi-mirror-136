# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['linkml_datalog',
 'linkml_datalog.dumpers',
 'linkml_datalog.engines',
 'linkml_datalog.generators',
 'linkml_datalog.model',
 'linkml_datalog.utils']

package_data = \
{'': ['*']}

install_requires = \
['linkml>=1.1.13,<2.0.0']

entry_points = \
{'console_scripts': ['linkml-dl = linkml_datalog.engines.datalog_engine:cli']}

setup_kwargs = {
    'name': 'linkml-datalog',
    'version': '0.2.0',
    'description': 'Datalog inference over LinkML schemas and data',
    'long_description': '# linkml-datalog\n\nValidation and inference over LinkML instance data using souffle\n\nDocumentation:\n\n * [linkml.io/linkml-datalog/](https://linkml.io/linkml-datalog/)\n',
    'author': 'cmungall',
    'author_email': 'cjm@berkeleybop.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/linkml/linkml-datalog',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
