# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['extended_int']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'extended-int',
    'version': '0.7',
    'description': 'Python classes that provides support for extended integers (the set of integers, and infinity).',
    'long_description': '=================\nExtended Integers\n=================\n.. image:: https://badge.fury.io/py/extended_int.svg\n    :target: https://badge.fury.io/py/extended_int\n\nThis repository provides a Python base class that implements extended integers.\n\nExample\n=======\n\n.. code-block:: python\n\n    In [1]: from numbers import Real, Integral\n\n    In [2]: from extended_int import ExtendedIntegral, int_inf\n\n    In [3]: float(int_inf)\n    Out[3]: inf\n\n    In [4]: print(int_inf)\n    inf\n\n    In [5]: int(int_inf)\n    ---------------------------------------------------------------------------\n    OverflowError                             Traceback (most recent call last)\n\n    In [6]: isinstance(int_inf, Real)\n    Out[6]: True\n\n    In [7]: isinstance(int_inf, Integral)\n    Out[7]: False\n\n\n    In [8]: isinstance(2.5, ExtendedIntegral)\n\n    Out[8]: False\n\n    In [9]: isinstance(int_inf, ExtendedIntegral)\n\n    Out[9]: True\n\n    In [10]: isinstance(2, ExtendedIntegral)\n\n    Out[10]: True\n',
    'author': 'Neil Girdhar',
    'author_email': 'mistersheik@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/NeilGirdhar/extended_int',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
