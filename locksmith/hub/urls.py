from django.conf.urls.defaults import *

urlpatterns = patterns('locksmith.hub.views',
    url(r'^report_calls/$', 'report_calls', name='report_calls'),
    url(r'^register/$', 'register', name='api_registration'),
    url(r'^confirmkey/(?P<key>[0-9a-f]{32})/$', 'confirm_registration',
        name='api_confirm'),
    url(r'^analytics/$', 'analytics_index', name='analytics_index'),
)

