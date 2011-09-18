# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.template.defaultfilters import filesizeformat

from limited.models import FileLib, Permission, Home, History, Link, LUser
from limited.utils import urlbilder

class AdminFileLib( admin.ModelAdmin ):
    """
    File lib admin with simple file size notes of trash and cache
    and links to clear it.
    """
    list_display = ( '__unicode__', 'get_cache', 'get_trash', )
    fieldsets = (
        ('Main', {
            'fields': ( 'name', 'description', 'path', )
        }),
        ('Advanced info', {
            'classes': ('wide',),
            'fields': ('cache', 'trash', )
        }),
    )
    readonly_fields = ( 'cache', 'trash', 'get_cache', 'get_trash', )

    def get_cache(self, obj):
        return filesizeformat( obj.get_cache_size( ) )
    get_cache.short_description = u'Cache size'

    def get_trash(self, obj):
        return filesizeformat( obj.get_trash_size( ) )
    get_trash.short_description = u'Trash size'

    def cache(self, obj):
        size = filesizeformat( obj.get_cache_size( ) )
        url = urlbilder( u'clear', obj.id, u'cache' )
        return u'{0} / <a href="{1}">clear</a>'.format( size, url )
    cache.short_description = 'Cache size'
    cache.allow_tags = True

    def trash(self, obj):
        size = filesizeformat( obj.get_trash_size( ) )
        url = urlbilder( u'clear', obj.id, u'trash' )
        return u'{0} / <a href="{1}">clear</a>'.format( size, url )
    trash.short_description = u'Trash size'
    trash.allow_tags = True

admin.site.register( FileLib, AdminFileLib )


class AdminPermission( admin.ModelAdmin ):
    list_display = ( 'id', 'edit', 'move', 'create', 'delete', 'upload', 'http_get', )
    list_filter = ( 'edit', 'move', 'create', 'delete', 'upload', 'http_get', )
    ordering = ('id',)
    

admin.site.register( Permission, AdminPermission )


class HomeForm( forms.ModelForm ):
    """
    Some hacks to represent permission like check boxes.
    If checked permits record not found it will be created.
    """
    # Override 'permission' to set it readonly
    perm_id = forms.CharField( widget=forms.TextInput( attrs={ 'readonly': 'readonly' } ), required=False )
    perm = forms.MultipleChoiceField(
        choices=[(i, i) for i in Permission.fields( )],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super( HomeForm, self ).__init__( *args, **kwargs )

        if kwargs.has_key( 'instance' ):
            # init data
            instance = kwargs['instance']
            self.initial['perm_id'] = instance.permission_id

            self.initial['perm'] = []
            permission = Permission.objects.get( id=instance.permission_id )
            # if Permission.{edit..} == true
            # append edit to init data
            for name in Permission.fields( ):
                if getattr( permission, name ):
                    self.initial['perm'].append( name )


    def save(self, commit=True):
        model = super( HomeForm, self ).save( commit=False )
        # Get checked names
        new = self.cleaned_data['perm']
        kwargs = { }
        # All array is False items
        # if name exist in new, set it True
        for item in Permission.fields( ):
            if item in new:
                kwargs[item] = True
            else:
                kwargs[item] = False

        model.permission = Permission.objects.get_or_create( **kwargs )[0]
        if commit:
            model.save( )
        return model

    class Meta:
        model = Home
        exclude = ('permission',)

class AdminHome( admin.ModelAdmin ):
    list_display = ( 'user', 'lib', 'permission', )
    list_filter = ( 'user', 'lib', )
    ordering = ('user',)
    form = HomeForm

admin.site.register( Home, AdminHome )


class AdminHistory( admin.ModelAdmin ):
    list_display = ( 'user', 'lib', 'type', 'time', )
    list_filter = ( 'time', 'user', 'lib', )
    readonly_fields = ( 'time', )

admin.site.register( History, AdminHistory )


class AdminLink( admin.ModelAdmin ):
    list_display = ( 'path', 'lib', 'hash', 'time', 'expires', )
    list_filter = ( 'time', )
    readonly_fields = ( 'time', )

admin.site.register( Link, AdminLink )


class HomeInline( admin.TabularInline ):
    model = Home
    raw_id_fields = ( "permission", )

class AdminUser( UserAdmin ):
    """
    Simple LUser with Home Inline
    """
    list_select_related = True
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', )
    fieldsets = (
    ('Main', { 'fields': ('username', 'password') }),
    ('Personal info', { 'fields': ('first_name', 'last_name', 'email') }),
    )
    readonly_fields = ( 'password', )
    inlines = [HomeInline, ]

    # Need to remove inlines when adding object
    def get_formsets(self, request, obj=None):
        if obj == None:
            return []
        return super(UserAdmin, self).get_formsets(request, obj=None)

admin.site.register( LUser, AdminUser )