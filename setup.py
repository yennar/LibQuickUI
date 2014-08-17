#!/usr/bin/env python

from distutils.core import setup

setup(name='LibQuickUI',
      version='1.0',
      description='UI Extension to PyQt',
      author='Yennar',
      url='https://github.com/yennar/LibQuickUI',
      package_dir = {'QuickUI': 'src/QuickUI'},
      packages=['QuickUI'],
     )
