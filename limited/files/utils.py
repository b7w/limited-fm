# -*- coding: utf-8 -*-

import logging
import threading
import time
from hashlib import md5

from django.db import transaction
from django.utils.encoding import smart_str

from limited import settings
from limited.files.storage import file_pre_change, FilePath

logger = logging.getLogger( __name__ )

class Thread:
    """
    Wrapper to run in a tread with commit_manually
    """

    def __init__(self, commit=True ):
        self.commit = commit

    def start(self, func, *args, **kwargs):
        """
        ``func`` - function, ``args`` and ``kwargs`` args for func
        """
        view = self.wrapper( func, *args, **kwargs )
        if self.commit:
            view = transaction.commit_manually( view )
        else:
            view = view
        threading.Thread( target=view )

    def wrapper(self, func, *args, **kwargs):
        """
        try except wrapper with logging and rollback
        """
        try:
            func( *args, **kwargs )
            if self.commit:
                transaction.commit()
        except Exception:
            logger.error( "Tread. args: {0}, kwargs:{1},".format( args, kwargs ) )
            if self.commit:
                transaction.rollback( )


class DownloadThread( threading.Thread ):
    """
    Wrapper to Download file in a thread.
    storage - FileStorage object,
    url - url link to download
    path -  path to the file where result would be save
    """

    def __init__(self, storage, url, file, *args, **kwargs ):
        super( DownloadThread, self ).__init__( *args, **kwargs )
        self.storage = storage
        self.url = url
        self.file = file

    def run(self):
        try:
            self.storage.download( self.url, self.file )
        except Exception as e:
            logger.error( u"DownloadThread. {0}. url:{1}, path:{2}".format( e, self.url, self.file ) )


class ZipThread( threading.Thread ):
    """
    Wrapper to Zip in a thread.
    storage - FileStorage object,
    path - path to the folder or file,
    file - path to the file where result would be save
    """

    def __init__(self, storage, path, file=None, *args, **kwargs ):
        super( ZipThread, self ).__init__( *args, **kwargs )
        self.storage = storage
        self.path = path
        self.file = file

    def run(self):
        try:
            self.storage.zip( self.path, self.file )
        except Exception as e:
            logger.error( u"ZipThread. {0}. path:{1}, zipfile:{2}".format( e, self.path, self.file ) )


class FileUnicName:
    """
    Create unic hash name for file
    """

    def __init__(self ):
        pass

    def hash(self, name):
        """
        Return md5 of "files.storage" + name
        """
        return md5( "files.storage" + smart_str( name ) ).hexdigest( )

    def time(self):
        return time.time()

    def build(self, path, time=None, extra=None):
        """
        return unic name of path + [extra]
        """
        full_name = settings.LIMITED_CACHE_PATH + path
        if time:
            full_name += str(time)
        if extra:
            full_name += str(extra)
        return self.hash( full_name )


def remove_cache( sender, **kwargs ):
    """
    Signal receiver function.
    It is delete cache files of all parent dirs
    if some files changed in directory.
    """
    HashBilder = FileUnicName( )
    lib = sender.lib
    dir = kwargs["basedir"]
    # if not system directories
    if not dir.startswith( settings.LIMITED_CACHE_PATH ) and dir != settings.LIMITED_TRASH_PATH:
        try:
            node = lib.cache.getName( *FilePath.split( dir ) )
            if node != None:
                node.setHash( HashBilder.time() )
                from limited.models import FileLib
                FileLib.objects.filter( id=lib.id ).update( cache=lib.cache )
        except Exception as e:
            logger.error( u"{0}. dir:{1}".format( e, dir ) )

file_pre_change.connect( remove_cache )