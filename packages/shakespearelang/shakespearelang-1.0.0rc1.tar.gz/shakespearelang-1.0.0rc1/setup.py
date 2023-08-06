# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shakespearelang', 'shakespearelang.tests']

package_data = \
{'': ['*'], 'shakespearelang.tests': ['sample_plays/*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'tatsu>=5.6.1,<5.7.0']

entry_points = \
{'console_scripts': ['shakespeare = shakespearelang.cli:main']}

setup_kwargs = {
    'name': 'shakespearelang',
    'version': '1.0.0rc1',
    'description': 'An interpreter for the Shakespeare Programming Language.',
    'long_description': "shakespearelang\n===============\n\n.. image:: https://codeclimate.com/github/zmbc/shakespearelang/badges/gpa.svg\n   :target: https://codeclimate.com/github/zmbc/shakespearelang\n   :alt: Code Climate\n\n.. image:: https://badge.fury.io/py/shakespearelang.svg\n   :target: https://badge.fury.io/py/shakespearelang\n   :alt: PyPI version\n\n\nA friendly interpreter for the Shakespeare Programming Language, implemented in\nPython.\n\nWhat is the Shakespeare Programming Language?\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\nThe Shakespeare Programming Language (SPL) is a programming language\nwith source code that looks like Shakespeare's plays. The language is\nTuring complete, so theoretically just as powerful as any other\nlanguage. It's a lot of fun to write but not very practical. More info can be\nfound `on Wikipedia`_.\n\nNote: Shakespeare's actual plays are not valid SPL. SPL does not aim to\nprovide backwards compatibility with legacy code written ~400 years ago.\n\nInstallation\n^^^^^^^^^^^^\n\n.. code-block::\n\n  pip install shakespearelang\n  # Or however else you install things. You do you.\n\nDocumentation\n^^^^^^^^^^^^^\n\nFor more on how to use shakespearelang, see `the docs`_.\n\nContributing\n^^^^^^^^^^^^\n\nYour contributions would be much appreciated! See `CONTRIBUTING.md`_.\n\n.. _on Wikipedia: https://en.wikipedia.org/wiki/Shakespeare_Programming_Language\n\n.. _the docs: https://shakespearelang.com/\n\n.. _CONTRIBUTING.md: https://github.com/zmbc/shakespearelang/blob/main/CONTRIBUTING.md\n",
    'author': 'Zeb Burke-Conte',
    'author_email': 'zebburkeconte@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://shakespearelang.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
