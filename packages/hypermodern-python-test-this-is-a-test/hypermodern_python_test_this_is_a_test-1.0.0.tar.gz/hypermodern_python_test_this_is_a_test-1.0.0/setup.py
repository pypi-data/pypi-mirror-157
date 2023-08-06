# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hypermodern_python_test_this_is_a_test']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'desert>=2020.11.18,<2021.0.0',
 'marshmallow>=3.17.0,<4.0.0',
 'nox>=2022.1.7,<2023.0.0',
 'requests>=2.28.0,<3.0.0']

extras_require = \
{':python_version < "3.9"': ['importlib-metadata>=4.12.0,<5.0.0']}

entry_points = \
{'console_scripts': ['hypermodern_python_test_this_is_a_test = '
                     'hypermodern_python_test_this_is_a_test.console:main']}

setup_kwargs = {
    'name': 'hypermodern-python-test-this-is-a-test',
    'version': '1.0.0',
    'description': 'Follow-along if hypermodern python project',
    'long_description': None,
    'author': 'John Ingles',
    'author_email': 'john.kenneth.ingles@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/john-ingles/hypermodern_python_test',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
