# -*- coding: utf-8 -*-

from hashlib import md5

from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.importlib import import_module

from limited.storage import FileStorage, FileNotExist, ZipThread

class DownloadManager:
    def __init__(self, lib):
        self.lib = lib
        self.storage = FileStorage( self.lib.get_path( ), self.lib.path )
        self.stpath = self.storage.path
        self.cache = { }

    def hash(self, path):
        """
        Return unic key for path
        """
        return md5( "download.manager" + smart_str( path ) ).hexdigest( )

    def cache_path(self, path):
        """
        Return path to the cache file.
        And cache it.
        """
        if self.cache.has_key( path ):
            return self.cache[path]
        cache = self.stpath.join( u".cache", self.hash( path ) )
        self.cache[path] = cache
        return cache

    def is_need_processing(self, path):
        """
        Check for directory if cache exist or size is small.
        Else return False
        """
        cache = self.cache_path( path )
        part = self.cache_path( path ) + u".part"
        if self.storage.exists( cache ) or self.storage.exists( part ):
            return False
        if self.storage.isdir( path ):
            size = self.storage.size( path, dir=True )
            max_size = getattr( settings, 'LIMITED_ZIP_HUGE_SIZE', 16 * 1024 ** 2 )
            if size > max_size:
                return True
        return False

    def process(self, path):
        if not self.storage.exists( u".cache" ):
            self.storage.mkdir( u".cache" )
        th = ZipThread( self.storage, path, self.cache_path( path ) )
        th.start( )

    def get_backend(self):
        import_path = settings.LIMITED_SERVE['BACKEND']
        dot = import_path.rindex( '.' )
        module, classname = import_path[:dot], import_path[dot + 1:]
        mod = import_module( module )
        return getattr( mod, classname )

    def build(self, path ):
        url_path = None
        if self.storage.isdir( path ):
            if not self.storage.exists( u".cache" ):
                self.storage.mkdir( u".cache" )
            if not self.storage.exists( self.cache_path( path ) ):
                self.storage.zip( path, self.cache_path( path ) )
            url_path = self.cache_path( path )
            name = self.stpath.name( path ) + '.zip'

        elif self.storage.isfile( path ):
            url_path = path
            name = self.stpath.name( path )
        else:
            raise FileNotExist( u"'%s' not found" % path )

        Backend = self.get_backend( )
        Response = Backend( self.storage, settings.LIMITED_SERVE )
        response = Response.generate( url_path, name )

        return response