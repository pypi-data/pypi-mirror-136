# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypet2bids']

package_data = \
{'': ['*']}

install_requires = \
['Gooey>=1.0.8,<2.0.0',
 'nibabel>=3.2.1,<4.0.0',
 'numpy>=1.21.3,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pydicom>=2.2.2,<3.0.0',
 'pyparsing>=3.0.4,<4.0.0',
 'pytest>=6.2.5,<7.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-dotenv>=0.19.1,<0.20.0',
 'scipy>=1.7.1,<2.0.0',
 'six>=1.16.0,<2.0.0']

entry_points = \
{'console_scripts': ['dcm2petbids = pypet2bids.dicom_convert:cli',
                     'pypet2bids = pypet2bids.cli:main']}

setup_kwargs = {
    'name': 'pypet2bids',
    'version': '0.0.6',
    'description': 'A python implementation of an ECAT to BIDS converter.',
    'long_description': None,
    'author': 'anthony galassi',
    'author_email': '28850131+bendhouseart@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.7.1,<3.10',
}


setup(**setup_kwargs)
