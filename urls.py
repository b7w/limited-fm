
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()

urlpatterns = patterns('',
    # Serve static
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes':True}),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'main.views.Index', name='index' ),
    url(r'^browser/$', 'main.views.Browser', name='browser' ),

    url(r'^download/$', 'main.views.Download', name='download' ),
    url(r'^upload/$', 'main.views.Upload', name='upload' ),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login' ),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout' ),
)