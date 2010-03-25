================
django-locksmith
================

Django utilities for shared api authentication & analytics.

django-locksmith provides two Django applications, locksmith.auth and locksmith.hub.
locksmith.hub is an application that facilitates signup and has generic analytics support that supports reports from any API
locksmith.auth provides mechanisms for being issued an API key from a hub server and authenticating API calls.  It also includes a management command to submit nightly reports to a locksmith.hub instance.

django-locksmith is a project of Sunlight Labs (c) 2010.  Written by James Turk <jturk@sunlightfoundation.com>.

All code is under a BSD-style license, see LICENSE for details.

Requirements
============

* python >= 2.5
* Django >= 1.2b1

locksmith.hub
==============

locksmith.hub provides several views, an authentication backend, and a management command.  A single instance of locksmith.hub can serve as the core of any number of related APIs.

Settings
--------

To use locksmith.hub it is necessary to add a few things to settings.py:

In ``INSTALLED_APPS`` add 'locksmith.hub'.

In ``AUTHENTICATION_BACKENDS`` add 'locksmith.hub.auth_backend.LocksmithBackend'

This will make the locksmith.hub models and management command available and allow users to sign in using their email and apikey.

Additionally there is one optional setting: ``LOCKSMITH_EMAIL_SUBJECT`` which if set will be used as the subject of the email sent when users request a key. (defaults to 'API Registration')

URLs
----

locksmith.hub provides two sets of URL patterns, one for registration and the other for analytics.

They can be added to your urls.py with the following line:

    (r'^', include('locksmith.hub.urls')),

This adds an accounts/ path that contains user-facing urls and an analytics/ path that adds analytics views that are only accessible by staff members.


locksmith.auth
==============

locksmith.auth provides URL endpoints and a management command that aim to make writing an API that gets its authentication details from a locksmith.hub instance as simple as possible.

Installation
------------

There are only two requirements to start using locksmith.auth:

* add 'locksmith.auth' to ``INSTALLED_APPS``
* add a line like: (r'^api/', include('locksmith.auth.urls')) to urls.py

If you have a Django model that is used to store your statistics you can define the following variables so that running ``./manage.py apireport`` can automatically generate statistics to send to the hub instance.

``LOCKSMITH_STATS_APP``
    application of the API log model (default: api)
``LOCKSMITH_STATS_MODEL``
    name of the API log model (default: LogEntry)
``LOCKSMITH_STATS_DATE_FIELD``
    name of the timestamp field on the log model (default: timestamp)
``LOCKSMITH_STATS_ENDPOINT_FIELD``
    name of the endpoint field on the log model (default: method)
``LOCKSMITH_STATS_USER_FIELD``
    name of the key field on the log model (default: caller_key)

You can optionally enable the ``APIKeyMiddleware`` by adding ``'locksmith.auth.middleware.APIKeyMiddleware`` to your ``MIDDLEWARE_CLASSES``.

Usage
-----

Adding ``'locksmith.auth.urls'`` to your urls.py exposes endpoints that a ``locksmith.hub`` instance will use to send API keys to you.

The ``locksmith.auth.models.ApiKey`` model is used to store information on the API key, when a user passes a key to your API you should check if such an ``ApiKey`` object exists and if it is active (ie. status='A') before serving the request.

Reporting Statistics
--------------------

To report usage of your API back to the ``locksmith.hub`` instance you can call ``./manage.py apireport`` daily.

See the ``LOCKSMITH_STATS_*`` settings documented above for details on having ``apireport`` find your API log model.

connecting a locksmith.hub and locksmith.auth instance
------------------------------------------------------

Assuming that you have a ``locksmith.hub`` instance and a ``locksmith.auth`` instance running as indicated above, the final step is to connect the two so that API signups become actual usable keys and analytics get back 

# hub: Add a new ``locksmith.hub.Api`` instance for the new API (choosing a name and signing key)
# hub: Push all existing keys to the new API's ``locksmith.auth`` endpoints by calling ``./manage.py pushkeys``

Assuming you already have a regular cronjob that pushes out new keys the new API will now get notified of new keys along with all of your other APIs.

TODO: document how non-locksmith.auth-enabled APIs can push to locksmith.hub
