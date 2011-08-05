
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'limited.views.IndexView', name='index' ),
    url(r'^lib(?P<id>\d+)/$', 'limited.views.FilesView', name='browser' ),
    url(r'^lib(?P<id>\d+)/trash/$', 'limited.views.TrashView', name='trash' ),
    url(r'^lib(?P<id>\d+)/history/$', 'limited.views.HistoryView', name='history' ),
    url(r'^lib(?P<id>\d+)/action/(?P<command>\w+)/$', 'limited.views.ActionView', name='action' ),

    url(r'^lib(?P<id>\d+)/download/$', 'limited.views.DownloadView', name='download' ),
    url(r'^lib(?P<id>\d+)/upload/$', 'limited.views.UploadView', name='upload' ),
    
    url(r'^link/(?P<hash>\w+)/$', 'limited.views.LinkView', name='link' ),
)