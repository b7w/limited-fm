# -*- coding: utf-8 -*-

import logging
import threading
import time
from hashlib import md5

from django.utils.encoding import smart_str

from limited import settings
from limited.files.api.base import file_pre_change
from limited.files.storage import FilePath


logger = logging.getLogger( __name__ )

class Thread( threading.Thread ):
    """
    Wrapper to run in a tread. Do not use Database updating!!!
    You will get ``TransactionManagementError``
    """

    def __init__(self, commit=False ):
        self.commit = commit
        self.view = None
        self.args = None
        self.kwargs = None
        threading.Thread.__init__( self )

    def setView(self, func, *args, **kwargs ):
        self.view = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.view( *self.args, **self.kwargs )
        except Exception as e:
            logger.error( "Tread. {0}. args: {1}, kwargs:{2},".format( e, *self.args, **self.kwargs ) )


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
        return time.time( )

    def build(self, path, time=None, extra=None):
        """
        return unic name of path + [extra]
        """
        full_name = settings.LIMITED_CACHE_PATH + path
        if time:
            full_name += str( time )
        if extra:
            full_name += str( extra )
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
                node.setHash( HashBilder.time( ) )
                from limited.models import FileLib

                FileLib.objects.filter( id=lib.id ).update( cache=lib.cache )
        except Exception as e:
            logger.error( u"{0}. dir:{1}".format( e, dir ) )

file_pre_change.connect( remove_cache )
