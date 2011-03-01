from django.conf.urls.defaults import *

urlpatterns = patterns('locksmith.mongoauth.views',
    url(r'^create_key/$', 'create_key', name='create_key'),
    url(r'^update_key/$', 'update_key', name='update_key'),
    url(r'^update_key_by_email/$', 'update_key', {'get_by':'email'},
        name='update_key_by_email'),
)

