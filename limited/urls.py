
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'limited.views.Index', name='index' ),
    url(r'^lib(?P<id>\d+)/$', 'limited.views.Browser', name='browser' ),
    url(r'^lib(?P<id>\d+)/trash/$', 'limited.views.Trash', name='trash' ),
    url(r'^lib(?P<id>\d+)/history/$', 'limited.views.History', name='history' ),
    url(r'^lib(?P<id>\d+)/action/(?P<command>\w+)/$', 'limited.views.Action', name='action' ),

    url(r'^lib(?P<id>\d+)/download/$', 'limited.views.Download', name='download' ),
    url(r'^lib(?P<id>\d+)/upload/$', 'limited.views.Upload', name='upload' ),
    
    url(r'^link/(?P<hash>\w+)/$', 'limited.views.Link', name='link' ),
)