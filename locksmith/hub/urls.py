from django.conf.urls.defaults import *

accounts = patterns('locksmith.hub.views',
    url(r'^register/$', 'register', name='api_registration'),
    url(r'^confirmkey/(?P<key>[0-9a-f]{32})/$', 'confirm_registration',
        name='api_confirm'),
)

analytics = patterns('locksmith.hub.views',
    url(r'^report_calls/$', 'report_calls', name='report_calls'),
    url(r'^$', 'analytics_index', name='analytics_index'),
)

urlpatterns = patterns('locksmith.hub.views',
    url(r'^accounts/', include(accounts)),
    url(r'^analytics/', include(analytics)),
)
