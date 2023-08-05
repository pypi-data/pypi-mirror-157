# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fiblat']

package_data = \
{'': ['*']}

install_requires = \
['numba>=0.55.2,<0.56.0', 'numpy>=1.18,<1.23']

setup_kwargs = {
    'name': 'fiblat',
    'version': '0.3.2',
    'description': 'A package for generating evenly distributed points on a sphere',
    'long_description': 'Fibonacci Lattice\n=================\n[![pypi](https://img.shields.io/pypi/v/fiblat)](https://pypi.org/project/fiblat/)\n[![build](https://github.com/erikbrinkman/fibonacci_lattice/actions/workflows/build.yml/badge.svg)](https://github.com/erikbrinkman/fibonacci_lattice/actions/workflows/build.yml)\n\nA simple small python package for generating uniform points on the sphere.\nThis module provides to functions `fiblat.cube_lattice` and `fiblat.sphere_lattice`.\nBoth functions take a dimension and a number of points and return numpy arrays that are roughly evenly spaced in either the `[0, 1]` hypercube or the unit hypersphere.\n\nInstallation\n------------\n\n```bash\npip install fiblat\n```\n\nUsage\n-----\n\n```python\nfrom fiblat import sphere_lattice, cube_lattice\n\ncube = cube_lattice(3, 100)\nsphere = sphere_lattice(3, 100)\n```\n\nDevelopment\n-----------\n\n- setup: `poetry install`\n- tests: `poetry run pytest && poetry run pyre`\n',
    'author': 'Erik Brinkman',
    'author_email': 'erik.brinkman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/erikbrinkman/fibonacci_lattice',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
