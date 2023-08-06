# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyroll',
 'pyroll.freiberg_flow_stress',
 'pyroll.freiberg_flow_stress.materials']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.2,<2.0.0', 'pyroll>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'pyroll-freiberg-flow-stress',
    'version': '1.1.0',
    'description': 'Plugin for PyRoll providing Freiberg flow stress approach and material database.',
    'long_description': '# PyRoll Freiberg Flow Stress Model\n\nPlugin for PyRoll providing Freiberg flow stress approach and a material database.\n\nFor the docs, see [here](docs/index.md).\n\nThis project is licensed under the [BSD-3-Clause license](LICENSE).\n\nThe package is available via PyPi and can be installed with\n\n    pip install pyroll-freiberg-flow-stress',
    'author': 'Max Weiner',
    'author_email': 'max.weiner@imf.tu-freiberg.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
