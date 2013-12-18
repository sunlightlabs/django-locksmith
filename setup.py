#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='django-locksmith',
      version='0.8.0',
      description='Django apps for API authentication and centralized authorization',
      author='James Turk',
      author_email='jturk@sunlightfoundation.com',
      license='BSD',
      url='http://github.com/sunlightlabs/django-locksmith/',
      packages=find_packages(),
      package_data={'locksmith': ['static/scripts/*.js', 'static/styles/*.css',
                                  'static/datatables/js/*.js', 'static/datatables/css/*.css',
                                  'static/datatables/images/*',
                                  'static/bootstrap/js/*.js', 'static/bootstrap/css/*.css',
                                  'static/bootstrap/img/*.png'],
                    'locksmith.hub': ['templates/locksmith/*.html', 'templates/locksmith/*.txt']},
)
