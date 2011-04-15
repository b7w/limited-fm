from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import datetime_safe
# Create your models here.

class PermissionError( Exception ):
    pass

class MPermission( models.Model ):
    edit = models.BooleanField( default=False )
    move = models.BooleanField( default=False )
    delete = models.BooleanField( default=False )
    create = models.BooleanField( default=False )
    upload = models.BooleanField( default=False )
    http_get = models.BooleanField( default=False )

    @classmethod
    def fields(self):
        return [k.name for k in self._meta.fields if k.name != 'id']

    class Meta:
        db_table = 'Permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __unicode__(self):
        name = 'ID' + str( self.id ) + ': '
        fields = self.fields()
        for item in fields:
            bool = getattr( self, item )
            name += item.capitalize() + ' ' + str(bool) + ', '
        return name


class MFileLib( models.Model ):
    name = models.CharField( max_length=64, null=False )
    path = models.CharField( max_length=256, null=False )

    class Meta:
        db_table = 'FileLib'
        verbose_name = 'File Lib'
        verbose_name_plural = 'File Libs'

    def __unicode__(self):
        return 'ID' + str( self.id ) + ': ' + str( self.name )


class MHome( models.Model ):
    user = models.ForeignKey( User )
    lib = models.ForeignKey( MFileLib )
    permission = models.ForeignKey( MPermission, default=1 )

    class Meta:
        db_table = 'Home'
        verbose_name = 'Home'
        verbose_name_plural = 'Home'

    def __unicode__(self):
        return 'ID' + str( self.id ) + ': ' + str( self.user ) + ', ' + str( self.lib )


class MHistory( models.Model ):
    ADD = 1
    CHANGE = 2
    DELETE = 3
    ACTION = (
    (ADD, 'add'),
    (CHANGE, 'change'),
    (DELETE, 'delete'),
    )
    user = models.ForeignKey( User )
    lib = models.ForeignKey( MFileLib )
    type = models.IntegerField( max_length=1, choices=ACTION )
    message = models.CharField( max_length=256, null=False )
    path = models.CharField( max_length=256, null=True )
    time = models.DateTimeField( auto_now_add=True, null=False )

    class Meta:
        db_table = 'History'
        verbose_name = 'History'
        verbose_name_plural = 'History'

    def __unicode__(self):
        return 'ID' + str( self.id ) + ': ' + str( self.user ) + ', ' + str( self.lib )


class MLink( models.Model ):
    hash = models.CharField( max_length=12, null=False )
    lib = models.ForeignKey( MFileLib )
    path = models.CharField( max_length=256, null=False )
    maxage = models.IntegerField( default=24*60*60, null=False )
    time = models.DateTimeField( auto_now_add=True, null=False )

    def expires(self):
        return timedelta(seconds=self.maxage)

    class Meta:
        db_table = 'Link'
        verbose_name = 'Link'
        verbose_name_plural = 'Links'

    def __unicode__(self):
        return 'ID' + str( self.id ) + ': ' + str( self.path ) + ', ' + str( self.time )