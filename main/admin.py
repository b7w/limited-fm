from django.contrib import admin

from main.models import MFileLib, MPermission, MHome, MHistory


class AdminFileLib( admin.ModelAdmin ):
    pass

admin.site.register( MFileLib, AdminFileLib )


class AdminPermission( admin.ModelAdmin ):
    list_display = ( 'id', 'edit', 'move', 'create', 'delete', 'upload', 'http_get', )
    list_filter = ( 'edit', 'move', 'create', 'delete', 'upload', 'http_get', )
    ordering = ('id',)

admin.site.register( MPermission, AdminPermission )


class AdminHome( admin.ModelAdmin ):
    pass

admin.site.register( MHome, AdminHome )


class AdminHistory( admin.ModelAdmin ):
    pass

admin.site.register( MHistory, AdminHistory )