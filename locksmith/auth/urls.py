from django.conf.urls.defaults import *

urlpatterns = patterns('locksmith.auth.views',
    url(r'^create_key/$', self.create_key_view, name='create_key'),
    url(r'^update_key/$', self.update_key_view, name='update_key'),
    url(r'^update_key_by_email/$', self.update_key_view, {'get_by':'email'},
        name='update_key_by_email'),
)

