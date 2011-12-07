# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^lib(?P<id>\d+)/images/$', 'lviewer.views.ImagesView', name='images' ),
    url(r'^lib(?P<id>\d+)/resize/(?P<size>\w+)/$', 'lviewer.views.ResizeView', name='resize' ),
)