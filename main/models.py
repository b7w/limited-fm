from django.contrib.auth.models import User
from django.db import models

# Create your models here.



class MPermission( models.Model ):
    edit = models.BooleanField( default=False )
    move = models.BooleanField( default=False )
    delete = models.BooleanField( default=False )
    create = models.BooleanField( default=False )
    upload = models.BooleanField( default=False )
    http_get = models.BooleanField( default=False )

    class Meta:
        db_table = 'Permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __unicode__(self):
        name = str( self.id ) + ': '
        fields = [k.name for k in self._meta.fields if k.name != 'id']
        for item in fields:
            bool = getattr( self, item )
            name += item[0].upper( )
            if bool: name += '1'
            else: name += '0'
            name += ', '
        return name


class MFileLib( models.Model ):
    name = models.CharField( max_length=64, null=False )
    path = models.CharField( max_length=256, null=False )

    class Meta:
        db_table = 'FileLib'
        verbose_name = 'File Lib'
        verbose_name_plural = 'File Libs'

    def __unicode__(self):
        return str( self.name )


class MHome( models.Model ):
    user = models.ForeignKey( User )
    lib = models.ForeignKey( MFileLib )
    permission = models.ForeignKey( MPermission, default=1 )
    
    class Meta:
        db_table = 'Home'
        verbose_name = 'Home'
        verbose_name_plural = 'Home'

    def __unicode__(self):
        return str( self.user ) + ' ' + str( self.lib )


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
        return str( self.user ) + ' ' + str( self.lib )