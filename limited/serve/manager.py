# -*- coding: utf-8 -*-

from django.utils.importlib import import_module

from limited import settings
from limited.files.storage import FileNotExist, FilePath
from limited.files.utils import FileUnicName, Thread


class DownloadManager:
    def __init__(self, lib):
        self.lib = lib
        self.storage = lib.getStorage( )
        self.Hash = FileUnicName( )
        self.cache = { }

    def cache_file(self, path):
        """
        Return path to the cache file.
        And cache it in dict.
        """
        if self.cache.has_key( path ):
            return self.cache[path]
        CacheDB = self.lib.cache.getName( *FilePath.split( path ) )
        time = None
        if CacheDB == None:
            time = self.Hash.time( )
            self.lib.cache.createName( time, *FilePath.split( path ) )
            self.lib.save( )
        else:
            time = CacheDB.hash
        hash = self.Hash.build( path, time=time )
        cache = FilePath.join( settings.LIMITED_CACHE_PATH, hash )
        self.cache[path] = cache
        return cache

    def is_need_processing(self, path):
        """
        Check for directory if cache exist or size is small.
        Else return False
        """
        if self.storage.isfile( path ):
            return False
        if self.storage.exists( self.cache_file( path ) ):
            return False
        if self.storage.isdir( path ):
            size = self.storage.size( path, dir=True, cached=False )
            max_size = settings.LIMITED_ZIP_HUGE_SIZE
            if size > max_size:
                return True
        return False

    def process(self, path):
        """
        Run ZipThread if there is no cache file ot cache part file.
        Create cache dir if not exists
        """
        if not self.storage.exists( settings.LIMITED_CACHE_PATH ):
            self.storage.mkdir( settings.LIMITED_CACHE_PATH )
        cache = self.cache_file( path )
        part = self.cache_file( path ) + u".part"
        if not self.storage.exists( cache ) and not self.storage.exists( part ):
            th = Thread( )
            th.setView( self.storage.extra.zip, path, self.cache_file( path ) )
            th.start( )

    def get_backend(self):
        """
        Return file serving backend
        """
        import_path = settings.LIMITED_SERVE['BACKEND']
        dot = import_path.rindex( '.' )
        module, classname = import_path[:dot], import_path[dot + 1:]
        mod = import_module( module )
        return getattr( mod, classname )

    def build(self, path ):
        """
        Return HttpResponse object with file
        or instruction to http server where file exists.
        Method don't check data size or anything else,
        archiving running for all data in main thread.
        So you have to check it manually with ``is_need_processing``
        """
        url_path = None
        if self.storage.isdir( path ):
            if not self.storage.exists( settings.LIMITED_CACHE_PATH ):
                self.storage.mkdir( settings.LIMITED_CACHE_PATH )
            if not self.storage.exists( self.cache_file( path ) ):
                self.storage.extra.zip( path, self.cache_file( path ) )
            url_path = self.cache_file( path )
            name = FilePath.name( path ) + '.zip'

        elif self.storage.isfile( path ):
            url_path = path
            name = FilePath.name( path )
        else:
            raise FileNotExist( u"'%s' not found" % path )

        Backend = self.get_backend( )
        Response = Backend( self.storage, settings.LIMITED_SERVE )
        response = Response.generate( url_path, name )

        return response