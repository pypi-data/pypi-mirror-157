# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydeflate', 'pydeflate.deflate', 'pydeflate.get_data', 'pydeflate.tools']

package_data = \
{'': ['*'], 'pydeflate': ['data/*']}

install_requires = \
['BeautifulSoup4>=4.11.1,<5.0.0',
 'pandas-datareader>=0.10.0,<0.11.0',
 'pyarrow>=8.0.0,<9.0.0',
 'requests>=2.28.1,<3.0.0',
 'weo>=0.7.3,<0.8.0',
 'wheel>=0.37.1,<0.38.0',
 'xlrd>=2.0.1,<3.0.0']

extras_require = \
{':extra == "dev"': ['numpy>=1.23.0,<2.0.0',
                     'country-converter>=0.7.4,<0.8.0',
                     'tox>=3.25.1,<4.0.0',
                     'twine>=4.0.1,<5.0.0',
                     'bump2version>=1.0.1,<2.0.0'],
 ':extra == "test" or extra == "dev"': ['pandas>=1.4.3,<2.0.0']}

setup_kwargs = {
    'name': 'pydeflate',
    'version': '1.1.3',
    'description': 'Package to convert current prices figures to constant prices and vice versa',
    'long_description': None,
    'author': 'Jorge Rivera',
    'author_email': 'jorge.rivera@one.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jm-rivera/pydeflate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
