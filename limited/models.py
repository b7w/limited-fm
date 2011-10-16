# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import hashlib

from limited import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import smart_str

from limited.fields import JsonTreeField
from limited.files.storage import FilePath, FileStorage

class PermissionError( Exception ):
    pass


class Permission( models.Model ):
    """
    Basic restrictions for files.
    Permits are not dependent on the file system.
    Base actions or boolean fields: edit,move,delete,create,upload,http_get
    """
    edit = models.BooleanField( default=False )
    move = models.BooleanField( default=False )
    delete = models.BooleanField( default=False )
    create = models.BooleanField( default=False )
    upload = models.BooleanField( default=False )
    http_get = models.BooleanField( default=False )

    @classmethod
    def fields(self):
        """
        Return names of field, except id.
        Generated for any count of fields.
        """
        return [k.name for k in self._meta.fields if k.name != 'id']

    @classmethod
    def full(self):
        """
        Return object with all fields equal True
        """
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
    """
    File lib represent some folder in file system.
    It have name, description, and path from LIMITED_ROOT_PATH
    """
    validators = [ RegexValidator(r"^\w+.*$","Path can start only with letters or numbers" ), ]

    name = models.CharField( max_length=64, null=False )
    description = models.CharField( max_length=256, null=False )
    path = models.CharField( max_length=256, null=False, validators=validators )
    cache = JsonTreeField( null=True, blank=True )

    def getStorage(self):
        return FileStorage( self )

    def get_path(self, root=None ):
        """
        Return absolute path.
        If root is None FileLib.path will be added to LIMITED_ROOT_PATH.
        """
        if root == None:
            root = settings.LIMITED_ROOT_PATH
        return FilePath.join( root, self.path )

    def get_cache_size(self):
        """
        Return size of a cache directory
        """
        File = self.getStorage()
        if File.isdir( settings.LIMITED_CACHE_PATH ):
            return File.size( settings.LIMITED_CACHE_PATH, dir=True  )
        return 0

    def get_trash_size(self):
        """
        Return size of a trash directory
        """
        File = self.getStorage()
        if File.isdir( settings.LIMITED_TRASH_PATH ):
            return File.size( settings.LIMITED_TRASH_PATH, dir=True  )
        return 0

    class Meta:
        verbose_name = 'File Lib'
        verbose_name_plural = 'File Libs'

    def __unicode__(self):
        return u'ID' + unicode( self.id ) + u': ' + unicode( self.name )


class Home( models.Model ):
    """
    Users home file libs with permission per lib.
    """
    user = models.ForeignKey( User )
    lib = models.ForeignKey( FileLib )
    permission = models.ForeignKey( Permission, default=1 )

    class Meta:
        verbose_name = 'Home'
        verbose_name_plural = 'Home'

    def __unicode__(self):
        return u'ID' + unicode( self.id ) + u': lib ' + unicode( self.lib.id ) + u', permission ' + unicode( self.permission.id )


class History( models.Model ):
    """
    Simple history for create,upload,rename,move,trash,delete,link.
    With path, extra path, user and file lib foreign keys.
    Extra path, for example for link action it is a url to object.
    """
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
    path = models.CharField( max_length=256, null=True, blank=True )
    extra = models.CharField( max_length=256, null=True, blank=True  )
    time = models.DateTimeField( auto_now_add=True, null=False )

    def get_image_type(self):
        """
        Return image type depend of ACTION
        """
        for key,val in self.image:
            if key == self.type:
                return val

    def is_extra(self):
        """
        If field extra is not empty
        """
        if self.extra:
            return True
        return False

    def get_extra(self):
        """
        Return html for extra field depend of type
        """
        if self.type == self.LINK:
            link = reverse( 'link', args=[self.extra] )
            return u"<a href=\"{0}\">direct link</a>".format( link )
        return None

    def hash(self):
        """
        Return FileStorage :func:`~limited.files.storage.FileStorage.hash` for file name
        """
        return FileStorage.hash( self.name )

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'History'

    def __unicode__(self):
        return u'ID' + unicode( self.id ) + u': ' + unicode( self.user ) + u', ' + unicode( self.lib )


class LinkManager( models.Manager ):
    """
    Object manager for simpler creating links
    and find them by hash
    """
    def add(self, lib, path, age=None, *args, **kwargs ):
        """
        Create new link with default LIMITED_LINK_MAX_AGE or age in seconds
        """
        if age == None:
            age = settings.LIMITED_LINK_MAX_AGE

        kwargs['lib'] = lib
        kwargs['path'] = path
        kwargs['hash'] = self.model.get_hash( lib.id, path )
        kwargs['expires'] = datetime.now( ) + timedelta( seconds=age )
        link = Link( *args, **kwargs )
        link.save( using=self._db )
        return link

    def find(self, hash ):
        """
        Find firs link by hash if it no expired
        else return None
        """
        links = self.get_query_set()\
            .filter( hash=hash, expires__gt=datetime.now() )\
            .order_by( '-time' )
        if len(links) > 0:
            return links[0]
        
        return None

class Link( models.Model ):
    """
    Link that provide a simple way to download file without having any permission.
    Store hash to find, path, expires DateTime, and lib lib foreign key.
    """
    hash = models.CharField( max_length=12, null=False )
    lib = models.ForeignKey( FileLib )
    path = models.CharField( max_length=256, null=False )
    expires = models.DateTimeField( null=False )
    time = models.DateTimeField( auto_now_add=True, null=False )

    objects = LinkManager()

    @classmethod
    def get_hash(self, lib_id, path ):
        """
        Return hash for link, need lib id and file path
        """
        return hashlib.md5( str(lib_id) + smart_str( path ) ).hexdigest( )[0:12]

    class Meta:
        verbose_name = 'Link'
        verbose_name_plural = 'Links'

    def __unicode__(self):
        return u'ID' + unicode( self.id ) + u': ' + unicode( self.path ) + u', ' + unicode( self.time )


class LUser( User ):
    """
    Simple proxy for django user with Home Inline.
    """
    class Meta:
        ordering = ["username"]
        proxy = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'