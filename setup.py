#!/usr/bin/env python

from distutils.core import setup

setup(name='django-locksmith',
      version='0.1.0',
      description='Django apps for API authentication and centralized authorization',
      author='James Turk',
      author_email='jturk@sunlightfoundation.com',
      license='BSD',
      url='http://github.com/sunlightlabs/django-locksmith/',
      packages=['locksmith', 'locksmith.auth', 'locksmith.auth.management',
                'locksmith.auth.management.commands', 'locksmith.common',
                'locksmith.common.management',
                'locksmith.common.management.commands', 'locksmith.hub']
)
