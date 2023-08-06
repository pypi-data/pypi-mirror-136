# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['vmeurisse_nitpick_styles']
install_requires = \
['nitpick==0.31.0']

setup_kwargs = {
    'name': 'vmeurisse-nitpick-styles',
    'version': '0.1.2',
    'description': 'Personal styles for nitpick',
    'long_description': '# Nitpick Styles\n\nThis repo contain my personal presets for [nitpick](https://github.com/andreoliwa/nitpick).\n',
    'author': 'Vincent Meurisse',
    'author_email': 'dev@meurisse.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
