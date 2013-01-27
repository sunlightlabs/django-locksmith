from django.conf.urls.defaults import *

accounts = patterns('locksmith.hub.views',
    url(r'^register/$', 'register', name='api_registration'),
    url(r'^resend/$', 'resend', name='resend'),
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^confirmkey/(?P<key>[0-9a-f]{32})/$', 'confirm_registration',
        name='api_confirm'),
)

analytics = patterns('locksmith.hub.views',
    url(r'^report_calls/$', 'report_calls', name='report_calls'),
    url(r'^reset_keys/$', 'reset_keys', name='reset_keys'),
    url(r'^$', 'analytics_index', name='analytics_index'),
    url(r'^new/$', 'new_analytics_index', name='new_analytics_index'),
    url(r'^new/api/(?P<api_name>[-\w]+)/$', 'new_api_analytics', name='new_api_analytics'),
    url(r'^new/keys/$', 'new_key_list', name='new_key_list'),
    url(r'^api/(?P<apiname>[-\w]+)/$', 'api_analytics', name='api_analytics'),
    url(r'^api/(?P<apiname>[-\w]+)/(?P<year>20[01]\d)/$', 'api_analytics', name='api_analytics_year'),
    url(r'^api/(?P<apiname>[-\w]+)/(?P<year>20[01]\d)/(?P<month>[01]?\d)/$', 'api_analytics', name='api_analytics_month'),
    url(r'^key/$', 'key_list', name='key_list'),
    url(r'^key/(?P<key>\w+)/$', 'key_analytics', name='key_analytics'),
)

analytics_data = patterns('locksmith.hub.dataviews',
    url(r'^data/apis/$', 'apis_list'),
    url(r'^data/api/(?P<api_id>\d+)/calls/$', 'calls_to_api'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/$', 'calls_to_api'),
    url(r'^data/apis/calls/$', 'api_calls'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/$', 'calls_to_api'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/yearly/$', 'calls_to_api_yearly'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/(?P<year>\d+)/$', 'calls_to_api_monthly'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/endpoint/$', 'calls_by_endpoint'),
    url(r'^data/api/(?P<api_name>[-\w]+)/callers/$', 'callers_of_api'),
    url(r'^data/keys/$', 'keys'),
    url(r'^data/keys/issued/$', 'keys_issued'),
    url(r'^data/keys/issued/yearly/$', 'keys_issued_yearly'),
    url(r'^data/keys/issued/(?P<year>\d+)/$', 'keys_issued_monthly'),
)

urlpatterns = patterns('locksmith.hub.views',
    url(r'^accounts/', include(accounts)),
    url(r'^analytics/', include(analytics)),
    url(r'^analytics/', include(analytics_data)),
)
