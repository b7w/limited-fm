from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin

from limited.models import FileLib, Permission, Home, History, Link, LUser


class AdminFileLib( admin.ModelAdmin ):
    pass

admin.site.register( FileLib, AdminFileLib )


class AdminPermission( admin.ModelAdmin ):
    list_display = ( 'id', 'edit', 'move', 'create', 'delete', 'upload', 'http_get', )
    list_filter = ( 'edit', 'move', 'create', 'delete', 'upload', 'http_get', )
    ordering = ('id',)
    

admin.site.register( Permission, AdminPermission )


class HomeForm( forms.ModelForm ):
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

admin.site.register( History, AdminHistory )


class AdminLink( admin.ModelAdmin ):
    list_display = ( 'path', 'lib', 'hash', 'expires', 'time', )
    list_filter = ( 'time', )

admin.site.register( Link, AdminLink )


class HomeInline( admin.TabularInline ):
    model = Home
    raw_id_fields = ( "permission", )

class AdminUser( UserAdmin ):
    list_select_related = True
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', )
    fieldsets = (
    ('Main', { 'fields': ('username', 'password') }),
    ('Personal info', { 'fields': ('first_name', 'last_name', 'email') }),
    )
    inlines = [HomeInline, ]

    # Need to remove inlines when adding object
    def get_formsets(self, request, obj=None):
        if obj == None:
            return []
        return super(UserAdmin, self).get_formsets(request, obj=None)

admin.site.register( LUser, AdminUser )