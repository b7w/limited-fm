# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url, include

from limited.core import settings
from limited.core.feeds import UserFeed, UserLibFeed

urlpatterns = patterns( '',
    url( r'^$', 'limited.core.views.IndexView', name='index' ),
    url( r'^lib(?P<id>\d+)/$', 'limited.core.views.FilesView', name='browser' ),
    url( r'^lib(?P<id>\d+)/trash/$', 'limited.core.views.TrashView', name='trash' ),
    url( r'^lib(?P<id>\d+)/history/$', 'limited.core.views.HistoryView', name='history' ),
    url( r'^lib(?P<id>\d+)/action/(?P<command>\w+)/$', 'limited.core.views.ActionView', name='action' ),
    url( r'^lib(?P<id>\d+)/clear/(?P<command>\w+)/$', 'limited.core.views.ActionClear', name='clear' ),

    url( r'^lib(?P<id>\d+)/download/$', 'limited.core.views.DownloadView', name='download' ),
    url( r'^lib(?P<id>\d+)/upload/$', 'limited.core.views.UploadView', name='upload' ),

    url( r'^link/(?P<hash>\w+)/$', 'limited.core.views.LinkView', name='link' ),

    url( r'^rss/user/$', UserFeed( ), name='rss.user.all' ),
    url( r'^rss/user/(?P<lib_id>\d+)/$', UserLibFeed( ), name='rss.user.lib' ),
)

if settings.LIMITED_LVIEWER:
    urlpatterns += patterns( '', url( r'^', include( 'limited.lviewer.urls' ) ), )