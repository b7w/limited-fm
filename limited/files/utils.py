# -*- coding: utf-8 -*-

import logging
import threading
import urllib

logger = logging.getLogger( __name__ )

class DownloadThread( threading.Thread ):
    """
    Download file in a thread
    """

    def __init__(self, storage, url, file, *args, **kwargs ):
        super( DownloadThread, self ).__init__( *args, **kwargs )
        self.storage = storage
        self.url = url
        self.file = file

    def run(self):
        try:
            from limited.files.base import FilePath
            path, name = FilePath.split( self.file )
            newfile = FilePath.join( path, u"[Downloading]" + name )
            urllib.urlretrieve( self.url, newfile )
            self.storage.rename( newfile, FilePath.name( self.file ) )
        except Exception as e:
            logger.error( u"DownloadThread. {0}. url:{1}, path:{2}".format( e, self.url, self.file ) )
            if self.storage.exists( self.file ):
                self.storage.remove( self.file )


class ZipThread( threading.Thread ):
    """
    Zip in a thread
    """

    def __init__(self, storage, path, file, *args, **kwargs ):
        super( ZipThread, self ).__init__( *args, **kwargs )
        self.storage = storage
        self.path = path
        self.file = file

    def run(self):
        try:
            from limited.files.base import FilePath
            tmp = self.file + u".part"
            self.storage.zip( self.path, tmp )
            self.storage.rename( tmp, FilePath.name( self.file ) )
        except Exception as e:
            logger.error( e )
            if self.storage.exists( tmp ):
                self.storage.remove( tmp )