# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['algn2pheno']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.79,<2.0',
 'numpy>=1.3,<2.0',
 'pandas>=1.3.5,<2.0.0',
 'readme',
 'repository',
 'sqlalchemy>=1.4.4,<2.0.0']

entry_points = \
{'console_scripts': ['algn2pheno = algn2pheno.__main__:main']}

setup_kwargs = {
    'name': 'algn2pheno',
    'version': '1.0.3',
    'description': 'A bioinformatics tool for rapid screening of genetic features (nt or aa changes) potentially linked to specific phenotypes',
    'long_description': None,
    'author': 'SantosJGND',
    'author_email': 'dourado.jns@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
