from django.conf.urls import *

accounts = patterns('locksmith.hub.views',
    url(r'^register/$', 'register', name='api_registration'),
    url(r'^resend/$', 'resend', name='resend'),
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^confirmkey/(?P<key>[0-9a-f]{32})/$', 'confirm_registration',
        name='api_confirm'),
    url(r'^checkkey/$', 'check_key', name='check_key'),
)

urlpatterns = patterns('locksmith.hub.views',
    url(r'^accounts/', include(accounts)),
)
