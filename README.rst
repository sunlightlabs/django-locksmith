================
django-locksmith
================

Django utilities for shared api authentication & analytics.

django-locksmith provides a few Django applications, locksmith.hub, locksmith.auth, and locksmith.mongoauth.

locksmith.hub is an application that facilitates signup and has generic analytics support that supports reports from any API

locksmith.auth provides mechanisms for being issued an API key from a hub server and authenticating API calls.  It also includes a management command to submit nightly reports to a locksmith.hub instance.

locksmith.mongoauth provies the same interface as locksmith.auth but instead of using Django's ORM it relies upon pymongo and uses a MongoDB database.  Like locksmith.auth it includes a way to submit nightly usage reports to a locksmith.hub instance.

django-locksmith is a project of Sunlight Labs (c) 2011.  Written by James Turk <jturk@sunlightfoundation.com>.

All code is under a BSD-style license, see LICENSE for details.

Requirements
============

For locksmith.hub:
* python >= 2.6
* Django >= 1.4
* South >= 0.7.6
* django-taggit
* celery >= 3.0.16

For locksmith.auth and locksmith.mongoauth:
* python >= 2.5
* Django >= 1.2

locksmith.hub
==============

locksmith.hub provides several views, an authentication backend, and a management command.  A single instance of locksmith.hub can serve as the core of any number of related APIs.

Settings
--------

To use locksmith.hub it is necessary to add a few things to settings.py:

In ``INSTALLED_APPS`` add 'locksmith.hub'.

In ``AUTHENTICATION_BACKENDS`` add 'locksmith.hub.auth_backend.LocksmithBackend'

This will make the locksmith.hub models and management command available and allow users to sign in using their email and apikey.

Optional settings:

``LOCKSMITH_EMAIL_SUBJECT``: if set will be used as the subject of the email sent when users request a key. (defaults to 'API Registration')
``LOCKSMITH_REPLICATED_APIS``: Locksmith has two key synchronization mechanisms. The older, stateful mechanism is used by default. To opt into using the newer, stateless mechanism for an API, add the name of the API here. This is a temporary setting. In 0.8 all APIs will use the new mechanism and this setting will prompt a deprecation warning.

Templates
---------
The locksmith.hub app provides a set of front-end templates that can be integrated into your website. To provide for maximum flexibility, these templates extend your project base template. You should specify the path to that base template using ``LOCKSMITH_BASE_TEMPLATE``. You should also specify a template to display when the user lacks authorization for the given view by setting ``LOCKSMITH_UNAUTHORIZED_TEMPLATE``.

Each of the locksmith.hub views allow you to specify a view to render instead of the default. This allows you to use {% include %} tags in both the base and top-level template. If you need to, you can override each view's template using these settings:

``LOCKSMITH_ANALYTICS_INDEX_TEMPLATE``
``LOCKSMITH_API_ANALYTICS_TEMPLATE``
``LOCKSMITH_KEY_ANALYTICS_TEMPLATE``
``LOCKSMITH_KEYS_LIST_TEMPLATE``
``LOCKSMITH_KEYS_LEADERBOARD_TEMPLATE``
``LOCKSMITH_REGISTER_TEMPLATE``

URLs
----

locksmith.hub provides two sets of URL patterns, one for registration and the other for analytics.

They can be added to your urls.py with the following line:

    (r'^', include('locksmith.hub.urls')),

This adds an accounts/ path that contains user-facing urls and an analytics/ path that adds analytics views that are only accessible by staff members.


locksmith.auth and locksmith.mongoauth
======================================

locksmith.auth and locksmith.mongoauth serve the same purpose and are basically interchangable.

Both apps provide URL endpoints and a management command that aim to make writing an API that gets its authentication details from a locksmith.hub instance as simple as possible.

In most places below they are interchangable and are denoted as ``locksmith.(mongo)auth``, use ``locksmith.mongoauth`` if you prefer your keys/logs to be stored in MongoDB, and use ``locksmith.auth`` if you prefer to use standard Django models.

Installation
------------

* add 'locksmith.(mongo)auth' to ``INSTALLED_APPS``
* add a line like: (r'^api/', include('locksmith.(mongo)auth.urls')) to urls.py

Add the following settings to your settings.py:

``LOCKSMITH_HUB_URL``
    URL to your locksmith.hub instance
``LOCKSMITH_SIGNING_KEY``
    signing key for this locksmith instance
``LOCKSMITH_API_NAME``
    name of this locksmith instance

You can optionally enable the ``APIKeyMiddleware`` by adding ``'locksmith.(mongo)auth.middleware.APIKeyMiddleware'`` to your ``MIDDLEWARE_CLASSES``.  This middleware makes use of two more optional settings:

``LOCKSMITH_QS_PARAM``
    Query String parameter to check for API key (default: apikey)
``LOCKSMITH_HTTP_HEADER``
    HTTP header to check for API key (default: HTTP_X_APIKEY)

locksmith.auth settings
~~~~~~~~~~~~~~~~~~~~~~~

If using locksmith.auth it is necessary to add a few extra settings to enable reporting statistics via ``./manage.py apireport``:

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

locksmith.mongoauth settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If using locksmith.mongoauth several settings can be provided to configure the MongoDB connection.

``LOCKSMITH_MONGO_HOST``
    address of mongodb server (default: localhost)
``LOCKSMITH_MONGO_PORT``
    port of mongodb server (default: 27017)
``LOCKSMITH_MONGO_DATABASE``
    name of mongodb database (default: locksmith)


Usage
-----

If using ``locksmith.auth`` the ``locksmith.auth.models.ApiKey`` model is used to store information on the API key. 

If using ``locksmith.mongoauth`` a collection named ``locksmith.keys`` will be created with '_id', 'status', and 'email' fields.

When a user passes a key to your API you should check if such an ``ApiKey`` object exists and if it is active (ie. status='A') before serving the request.  This check is handled automatically if you are using the provided ``APIKeyMiddleware``.

Reporting Statistics
--------------------

To report usage of your API back to the ``locksmith.hub`` instance you can call ``./manage.py apireport`` daily.

connecting a locksmith.hub and locksmith.auth instance
------------------------------------------------------

Assuming that you have a ``locksmith.hub`` instance and a ``locksmith.(mongo)auth`` instance running as indicated above, the final step is to connect the two so that API signups become actual usable keys and analytics get back.

# hub: Add a new ``locksmith.hub.Api`` instance for the new API (choosing a name and signing key)
# hub: Push all existing keys to the new API's locksmith auth endpoints by calling ``./manage.py pushkeys``

Assuming you already have a regular cronjob that pushes out new keys the new API will now get notified of new keys along with all of your other APIs.

TODO: document how non-locksmith.auth-enabled APIs can push to locksmith.hub
