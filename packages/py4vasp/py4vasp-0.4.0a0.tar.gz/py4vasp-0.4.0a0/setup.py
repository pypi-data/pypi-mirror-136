# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['py4vasp',
 'py4vasp._third_party',
 'py4vasp._util',
 'py4vasp.control',
 'py4vasp.data',
 'py4vasp.exceptions',
 'py4vasp.raw']

package_data = \
{'': ['*']}

install_requires = \
['ase>=3.19.0,<4.0.0',
 'h5py>=3.3.0,<4.0.0',
 'kaleido>=0.2.1,<0.3.0,!=0.2.1.post1',
 'mdtraj>=1.9.5,<2.0.0',
 'mrcfile>=1.2.0,<2.0.0',
 'nglview>=3.0.3,<4.0.0',
 'numpy>=1.17.4,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'plotly>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'py4vasp',
    'version': '0.4.0a0',
    'description': 'Tool for assisting with the analysis and setup of VASP calculations.',
    'long_description': None,
    'author': 'Martin Schlipf',
    'author_email': 'martin.schlipf@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
