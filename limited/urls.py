
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'limited.views.Index', name='index' ),
    url(r'^browser/$', 'limited.views.Browser', name='browser' ),
    url(r'^action/(?P<command>\w+)/$', 'limited.views.Action', name='action' ),

    url(r'^download/$', 'limited.views.Download', name='download' ),
    url(r'^link/(?P<hash>\w+)/$', 'limited.views.Link', name='link' ),
    url(r'^upload/$', 'limited.views.Upload', name='upload' ),
)