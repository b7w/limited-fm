from datetime import timedelta
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
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
        fields = self.fields( )
        for item in fields:
            bool = getattr( self, item )
            name += item.capitalize( ) + ' ' + str( bool ) + ', '
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
    lib = models.ForeignKey( MFileLib )
    type = models.IntegerField( max_length=1, choices=ACTION )
    name = models.CharField( max_length=256, null=False )
    path = models.CharField( max_length=256, null=True )
    extra = models.CharField( max_length=256, null=True )
    time = models.DateTimeField( auto_now_add=True, null=False )

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
    
    def get_extra(self):
        if self.type == self.LINK:
            return self.get_link()
        return False

    def get_link(self):
        return reverse('link', args=[self.extra])

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
    maxage = models.IntegerField( default=24 * 60 * 60, null=False )
    time = models.DateTimeField( auto_now_add=True, null=False )

    def expires(self):
        return timedelta( seconds=self.maxage )

    class Meta:
        db_table = 'Link'
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