from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover( )

urlpatterns = patterns( '',
    # Serve static
    url( r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True} ),

    url( r'^', include( 'limited.core.urls' ) ),

    url( r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'limited/login.html'}, name='login' ),
    url( r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout' ),

    # Uncomment the next line to enable the admin:
    url( r'^admin/doc/', include( 'django.contrib.admindocs.urls' ) ),
    url( r'^admin/', include( admin.site.urls ) ),
)