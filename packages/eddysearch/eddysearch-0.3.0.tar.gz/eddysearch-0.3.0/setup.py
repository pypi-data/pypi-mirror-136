# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eddysearch', 'eddysearch.search']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.3,<4.0', 'numpy>=1.18,<2.0']

setup_kwargs = {
    'name': 'eddysearch',
    'version': '0.3.0',
    'description': '',
    'long_description': "# EddySearch  [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Python 3.6](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) ![Tests](https://github.com/innvariant/eddysearch/workflows/Tests/badge.svg)\nEddy is a collection of artificial function landscapes and search strategies to find their extrema points.\nMost artificial landscapes are in euclidean space and can simply be seen as a landscape of hills and valleys and the goal is to find the lowest or highest point within a given evaluation budget.\nThis gives the possibility to compare optimization methods -- or often also known as search strategies -- in artificial settings:\neither for the curious mind, for pedagogical purpose or for fair experimental comparison.\nYou can simply extend it with your own search strategy and see how well it works in these landscapes (objective functions).\n\n**Jump to ..**\n- [Installation](#installation)\n- [Introduction / Overview](#intro)\n\n# Installation\n- Install from PyPi via poetry: ``poetry install eddysearch``\n- Install with pip: ``pip install eddysearch``\n- Install latest development version: ``poetry add git+https://github.com/innvariant/eddysearch.git#master``\n\n# Intro\nTo make visualizations (e.g. 3D Plots or Manim-Videos) easy, objectives define much more information than just the pure function definition.\nFor example, they contain information about suggested visualization boundaries or their analytical or empirical known extrema.\nSearch strategies on the other hand provide capabilities to track their search path through space.\nSo it is easy to follow their search principles.\nThe main intent is to provide insights into the differences of various search strategies and how they behave in different artifcial landscapes.\n\n![Random Search over Himmelblau objective](res/himmelblau-random.png)\n![CMA-ES Search over Himmelblau objective](res/himmelblau-cmaes.png)\n![Adam Gradient Descent over Himmelblau objective](res/himmelblau-adam.png)\n![Random Search over Rastrigin objective](res/rastrigin-random.png)\n\n\n\n# Artificial Landscapes\n.. also called [test functions for optimization on Wikipedia](https://en.wikipedia.org/wiki/Test_functions_for_optimization).\n\n\n### Himmelblau Function\nAlso see [Wikipedia: Himmelblau's function](https://en.wikipedia.org/wiki/Himmelblau%27s_function).\n\n$`f(x,y) = (x^2+y-11(x+ y^2-7)^2)`$\n\n```python\nfrom eddysearch.objective import HimmelblauObjective\n\nobj = HimmelblauObjective()\n```\n\n\n\n### RastriginObjective\n\n```python\nfrom eddysearch.objective import RastriginObjective\n\nobj = RastriginObjective()\n```\n\n### RosenbrockObjective\n\n```python\nfrom eddysearch.objective import RosenbrockObjective\n\nobj = RosenbrockObjective()\n```\n\n\n### LeviN13Objective\n\n```python\nfrom eddysearch.objective import LeviN13Objective\n\nobj = LeviN13Objective()\n```\n\n\n### CrossInTrayObjective\n\n```python\nfrom eddysearch.objective import CrossInTrayObjective\n\nobj = CrossInTrayObjective()\n```\n\n\n### EggholderObjective\n```python\nfrom eddysearch.objective import EggholderObjective\n\nobj = EggholderObjective()\n```\n\n### Under Development\n* Stier2020A1Objective\n```python\nfrom eddysearch.objective import Stier2020A1Objective\n\nobj = Stier2020A1Objective()\n```\n\n* Stier2020A2Objective\n```python\nfrom eddysearch.objective import Stier2020A2Objective\n\nobj = Stier2020A2Objective()\n```\n\n* Stier2020BObjective\n```python\nfrom eddysearch.objective import Stier2020BObjective\n\nobj = Stier2020BObjective()\n```\n",
    'author': 'Julian Stier',
    'author_email': 'julian.stier@uni-passau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/innvariant/eddy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
