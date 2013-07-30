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
    url(r'^keys/$', 'key_list', name='key_list'),
    url(r'^keys/leaderboard/$', 'keys_leaderboard', name="keys_leaderboard"),
    url(r'^keys/leaderboard/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'keys_leaderboard'),
    url(r'^keys/leaderboard/(?P<api_name>[-\w]+)/$', 'keys_leaderboard'),
    url(r'^keys/leaderboard/(?P<api_name>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'keys_leaderboard'),
    url(r'^keys/(?P<api_name>[-\w]+)/leaderboard/$', 'keys_leaderboard'),
    url(r'^api/(?P<api_name>[-\w]+)/$', 'api_analytics', name='api_analytics'),
    url(r'^key/(?P<key>\w+)/$', 'key_analytics', name='key_analytics'),
)

analytics_data = patterns('locksmith.hub.dataviews',
    url(r'^data/apis/$', 'apis_list',
        name='api-list'),
    url(r'^data/api/(?P<api_id>\d+)/calls/$', 'calls_to_api',
        name='calls-to-api'),
    url(r'^data/calls/$', 'all_calls', name='all-calls'),
    url(r'^data/calls/monthly/$', 'api_calls_monthly',
        name='api-calls-monthly'),
    url(r'^data/calls/daily/$', 'api_calls_daily',
        name='api-calls-daily'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/$', 'calls_to_api'),
    url(r'^data/apis/calls/$', 'api_calls',
        name='apis-by-calls'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/$', 'calls_to_api'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/yearly/$', 'calls_to_api_yearly',
        name='calls-to-api-yearly'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/monthly/$', 'calls_to_api_monthly',
        name='calls-to-api-monthly'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/daily/$', 'calls_to_api_daily',
        name='calls-to-api-daily'),
    url(r'^data/api/(?P<api_name>[-\w]+)/calls/endpoint/$', 'calls_by_endpoint',
        name='calls-to-api-by-endpoint'),
    url(r'^data/api/(?P<api_name>[-\w]+)/callers/$', 'callers_of_api',
        name='callers-of-api'),
    url(r'^data/calls/range', 'calls_range', name='calls-range'),
    url(r'^data/keys/$', 'keys'),
    url(r'^data/keys/issued/$', 'keys_issued'),
    url(r'^data/keys/issued/yearly/$', 'keys_issued_yearly',
        name='keys-issued-yearly'),
    url(r'^data/keys/issued/monthly/$', 'keys_issued_monthly',
        name='keys-issued-monthly'),
    url(r'^data/key/(?P<key_uuid>\w+)/calls/yearly/$', 'calls_from_key_yearly',
        name='calls-from-key-yearly'),
    url(r'^data/key/(?P<key_uuid>\w+)/calls/monthly/$', 'calls_from_key_monthly',
        name='calls-from-key-monthly'),
    url(r'^data/key/(?P<key_uuid>\w+)/calls/endpoint/$', 'calls_from_key_by_endpoint',
        name='calls-from-key-by-endpoint'),
    url(r'^data/keys/leaderboard/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'quarterly_leaderboard'),
    url(r'^data/keys/leaderboard/(?P<api_name>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'quarterly_leaderboard'),
)

urlpatterns = patterns('locksmith.hub.views',
    url(r'^accounts/', include(accounts)),
    url(r'^analytics/', include(analytics)),
    url(r'^analytics/', include(analytics_data)),
)
