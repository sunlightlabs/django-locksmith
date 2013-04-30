#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='django-locksmith',
      version='0.7.0',
      description='Django apps for API authentication and centralized authorization',
      author='James Turk',
      author_email='jturk@sunlightfoundation.com',
      license='BSD',
      url='http://github.com/sunlightlabs/django-locksmith/',
      packages=find_packages(),
      package_data={'locksmith': ['media/scripts/*.js'],
                    'locksmith.hub': ['templates/locksmith/*.html']},
)
