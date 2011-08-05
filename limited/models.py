from datetime import timedelta
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
# Create your models here.
from limited.storage import StoragePath

class PermissionError( Exception ):
    pass


class Permission( models.Model ):
    edit = models.BooleanField( default=False )
    move = models.BooleanField( default=False )
    delete = models.BooleanField( default=False )
    create = models.BooleanField( default=False )
    upload = models.BooleanField( default=False )
    http_get = models.BooleanField( default=False )

    # Return names of boolean fields ( not id )
    # generated depending on the number of fields
    @classmethod
    def fields(self):
        return [k.name for k in self._meta.fields if k.name != 'id']

    # Return all True
    # generated depending on the number of fields
    @classmethod
    def Full(self):
        fieldcount = len(self._meta.fields)-1
        fields = self.fields()
        perm = Permission()
        for l in range( fieldcount ):
            setattr( perm, fields[l], True )
        return perm

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __unicode__(self):
        name = 'ID' + str( self.id ) + ': '
        fields = self.fields( )
        for item in fields:
            bool = getattr( self, item )
            name += item.capitalize( ) + ' ' + str( bool ) + ', '
        return name


class FileLib( models.Model ):
    validators = [ RegexValidator(r"^\w+.*$","Path can start only with letters or numbers" ), ]

    name = models.CharField( max_length=64, null=False )
    description = models.CharField( max_length=256, null=False )
    path = models.CharField( max_length=256, null=False, validators=validators )

    def get_path(self):
        return StoragePath().join( settings.LIMITED_ROOT_PATH, self.path )

    class Meta:
        verbose_name = 'File Lib'
        verbose_name_plural = 'File Libs'

    def __unicode__(self):
        return 'ID' + str( self.id ) + ': ' + str( self.name )


class Home( models.Model ):
    user = models.ForeignKey( User )
    lib = models.ForeignKey( FileLib )
    permission = models.ForeignKey( Permission, default=1 )

    class Meta:
        verbose_name = 'Home'
        verbose_name_plural = 'Home'

    def __unicode__(self):
        return 'ID' + str( self.id ) + ': ' + str( self.user ) + ', ' + str( self.lib )


class History( models.Model ):
    CREATE = 1
    UPLOAD = 2
    RENAME = 3
    MOVE = 4
    TRASH = 5
    DELETE = 6
    LINK = 7
    ACTION = (
            (CREATE, 'create'),
            (UPLOAD, 'upload'),
            (RENAME, 'rename'),
            (MOVE, 'move'),
            (TRASH, 'trash'),
            (DELETE, 'delete'),
            (LINK, 'link'),
        )
    image = (
            (CREATE, 'create'),
            (UPLOAD, 'create'),
            (RENAME, 'rename'),
            (MOVE, 'move'),
            (TRASH, 'trash'),
            (DELETE, 'delete'),
            (LINK, 'create'),
        )
    user = models.ForeignKey( User )
    lib = models.ForeignKey( FileLib )
    type = models.IntegerField( max_length=1, choices=ACTION )
    name = models.CharField( max_length=256, null=False )
    path = models.CharField( max_length=256, null=True )
    extra = models.CharField( max_length=256, null=True )
    time = models.DateTimeField( auto_now_add=True, null=False )

    # Return image type
    # depend of ACTION
    def get_image_type(self):
        for key,val in self.image:
            if key == self.type:
                return val

    def get_message(self):
        return "{0}, {1}".format( self.name, self.get_type_display())
    message = property(get_message)

    def is_extra(self):
        if self.extra:
            return True
        return False

    # Return html for extra field
    # depend of type
    def get_extra(self):
        if self.type == self.LINK:
            link = reverse( 'link', args=[self.extra] )
            return "<a href=\"{0}\">direct link</a>".format( link )
        return False

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'History'

    def __unicode__(self):
        return 'ID' + str( self.id ) + ': ' + str( self.user ) + ', ' + str( self.lib )


class Link( models.Model ):
    hash = models.CharField( max_length=12, null=False )
    lib = models.ForeignKey( FileLib )
    path = models.CharField( max_length=256, null=False )
    maxage = models.IntegerField( default=24 * 60 * 60, null=False )
    time = models.DateTimeField( auto_now_add=True, null=False )

    def expires(self):
        return timedelta( seconds=self.maxage )

    class Meta:
        verbose_name = 'Link'
        verbose_name_plural = 'Links'

    def __unicode__(self):
        return 'ID' + str( self.id ) + ': ' + str( self.path ) + ', ' + str( self.time )


class LUser( User ):
    class Meta:
        ordering = ["username"]
        proxy = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'