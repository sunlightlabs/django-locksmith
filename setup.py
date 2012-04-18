#!/usr/bin/env python

from distutils.core import setup

setup(name='django-locksmith',
      version='0.6.0',
      description='Django apps for API authentication and centralized authorization',
      author='James Turk',
      author_email='jturk@sunlightfoundation.com',
      license='BSD',
      url='http://github.com/sunlightlabs/django-locksmith/',
      packages=['locksmith', 'locksmith.auth', 'locksmith.auth.management',
                'locksmith.auth.management.commands', 'locksmith.hub',
                'locksmith.hub.management', 'locksmith.hub.management.commands',
                'locksmith.hub.templatetags', 'locksmith.mongoauth',
                'locksmith.mongoauth.management',
                'locksmith.mongoauth.management.commands'],
      package_data={'locksmith': ['media/scripts/*.js'],
                    'locksmith.hub': ['templates/locksmith/*.html']},
)
