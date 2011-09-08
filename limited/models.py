# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import hashlib

from limited import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import smart_str

from limited.files.storage import FilePath, FileStorage

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

    def get_path(self, root=None ):
        if root == None:
            root = settings.LIMITED_ROOT_PATH
        return FilePath.join( root, self.path )

    def get_cache_size(self):
        File = FileStorage( self.get_path() )
        return File.size( settings.LIMITED_CACHE_PATH, dir=True  )

    def get_trash_size(self):
        File = FileStorage( self.get_path() )
        return File.size( settings.LIMITED_TRASH_PATH, dir=True  )

    class Meta:
        verbose_name = 'File Lib'
        verbose_name_plural = 'File Libs'

    def __unicode__(self):
        return u'ID' + unicode( self.id ) + u': ' + unicode( self.name )


class Home( models.Model ):
    user = models.ForeignKey( User )
    lib = models.ForeignKey( FileLib )
    permission = models.ForeignKey( Permission, default=1 )

    class Meta:
        verbose_name = 'Home'
        verbose_name_plural = 'Home'

    def __unicode__(self):
        return u'ID' + unicode( self.id ) + u': ' + unicode( self.user ) + u', ' + unicode( self.lib )


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
    path = models.CharField( max_length=256, null=True, blank=True )
    extra = models.CharField( max_length=256, null=True, blank=True  )
    time = models.DateTimeField( auto_now_add=True, null=False )

    # Return image type
    # depend of ACTION
    def get_image_type(self):
        for key,val in self.image:
            if key == self.type:
                return val

    def is_extra(self):
        if self.extra:
            return True
        return False

    # Return html for extra field
    # depend of type
    def get_extra(self):
        if self.type == self.LINK:
            link = reverse( 'link', args=[self.extra] )
            return u"<a href=\"{0}\">direct link</a>".format( link )
        return None

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'History'

    def __unicode__(self):
        return u'ID' + unicode( self.id ) + u': ' + unicode( self.user ) + u', ' + unicode( self.lib )


class LinkManager( models.Manager ):
    def add(self, lib, path, age=None, *args, **kwargs ):
        """
        Create new link with default age 24h
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
    hash = models.CharField( max_length=12, null=False )
    lib = models.ForeignKey( FileLib )
    path = models.CharField( max_length=256, null=False )
    expires = models.DateTimeField( null=False )
    time = models.DateTimeField( auto_now_add=True, null=False )

    objects = LinkManager()

    @classmethod
    def get_hash(self, lib_id, path ):
        """ Return hash for link, need lib id and file path"""
        return hashlib.md5( str(lib_id) + smart_str( path ) ).hexdigest( )[0:12]

    class Meta:
        verbose_name = 'Link'
        verbose_name_plural = 'Links'

    def __unicode__(self):
        return u'ID' + unicode( self.id ) + u': ' + unicode( self.path ) + u', ' + unicode( self.time )


class LUser( User ):
    class Meta:
        ordering = ["username"]
        proxy = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'