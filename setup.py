#!/usr/bin/env python

from distutils.core import setup

setup(name='crawler',
      version='0.1',
      description='Python Crawler',
      author='Peter Ruibal',
      author_email='ruibalp@gmail.com',
      url='https://github.com/fmoo/python-crawler',
      packages=['crawler'],
      requires=['pycurl', 'html5lib', 'routes', 'lxml'],
     )
