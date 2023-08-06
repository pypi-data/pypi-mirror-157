# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['otlet_test_project']

package_data = \
{'': ['*']}

install_requires = \
['pygame', 'sphinx[lint]>=5.0.2,<6.0.0']

extras_require = \
{':os_name == "posix"': ['otlet>=1.0.0rc1,<2.0.0'],
 ':platform_machine == "aarch64" and platform_python_implementation == "CPython"': ['django>=4.0.3,<5.0.0'],
 ':sys_platform == "linux" and os_name == "posix"': ['otlet-cli>=1.0.0rc4,<2.0.0'],
 'alleniverson:python_version >= "3.7"': ['tensorflow>=2.9.1,<3.0.0']}

setup_kwargs = {
    'name': 'otlet-test-project',
    'version': '0.0.3',
    'description': 'do not download. for testing purposes only.',
    'long_description': None,
    'author': 'kevinshome',
    'author_email': 'noah.tanner7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.0,<4.0',
}


setup(**setup_kwargs)
