# -*- coding: utf-8 -*-

import logging
import os
import threading
import time
from hashlib import md5

from django.utils.encoding import smart_str

from limited.core import settings

logger = logging.getLogger( __name__ )

class FilePath( object ):
    """
    Wrapper for ``os.path`` for working with file paths.
    The class is static, no needed to create instance.
    """
    @staticmethod
    def join( path, name ):
        """
        Concatenate to paths
        """
        if len( name ) > 1 and name[0] == u'/':
            name = name[1:]
        return os.path.join( path, name )

    @staticmethod
    def name(path):
        """
        return file name or ''
        """
        return os.path.basename( path )

    @staticmethod
    def dirname( path ):
        """
        return directory path of file
        or return path if ends with '/'
        """
        return os.path.dirname( path )

    @staticmethod
    def norm( path ):
        """
        If src include '../' or './' normalise it
        """
        path = os.path.normpath( path )
        if path == u'.':
            return u''
        return path

    @staticmethod
    def check( path, norm=False ):
        """
        Check is path has some strange sub strings after FilePath.norm
        like '../', '/', '.'
        if find - return False
        if norm=True, than path = FilePath.norm( path ). By default is False
        """
        if norm == True:
            path = FilePath.norm( path )
        if path.startswith( u'/' ):
            return False
        elif u".." in path:
            return False
        return True

    @staticmethod
    def split( path ):
        """
        Split path
        """
        if len( path ) > 1 and path[0] == '/':
            path = path[1:]
        if len( path ) > 1 and path[-1] == '/':
            path = path[:-1]
        return path.split( '/' )


class Thread( threading.Thread ):
    """
    Wrapper to run in a tread. Do not use Database updating in thread!!!
    You will get ``TransactionManagementError``

    >>> T = Thread( )
    >>> T.setView( Storage.extra.download, url, path, signal=False )
    >>> T.start( )
    """

    def __init__(self):
        threading.Thread.__init__( self )
        self.view = None
        self.args = None
        self.kwargs = None

    def setView(self, func, *args, **kwargs ):
        """
        Set link to function and args, kwargs
        """
        self.view = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Thread body with catching all exceptions and log them
        """
        try:
            self.view( *self.args, **self.kwargs )
        except Exception as e:
            logger.error( "Tread. {0}. args: {1}, kwargs:{2},".format( e, *self.args, **self.kwargs ) )


class FileUnicName:
    """
    Create unic hash name for file

    >>> from limited.core.files.utils import *
    >>> builder = FileUnicName( )
    >>> time = builder.time()
    >>> time
    1323242186.620497
    >>> builder.build( "some/file", time=time )
    'fb41bb28d2614159246163f8dc77ac14'
    >>> builder.build( "some/file", time=builder.time() )
    '6ef61d7c41d391fcd17dd59e1d29dfc2'
    >>> builder.build( "some/file", time=time, extra='tag1' )
    'bb89a8697e7f2acfd5d904bc96ce5b81'
    """

    def __init__(self ):
        pass

    def hash(self, name):
        """
        Return md5 of "files.storage" + name
        """
        return md5( "files.storage" + smart_str( name ) ).hexdigest( )

    def time(self):
        """
        Return just time.time( )
        """
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
