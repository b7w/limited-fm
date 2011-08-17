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
        newfile = None
        try:
            from limited.files.storage import FilePath
            newfile = self.file + u".part"
            urllib.urlretrieve( self.url, self.storage.abspath( newfile ) )
            self.storage.rename( newfile, FilePath.name( self.file ) )
        except Exception as e:
            logger.error( u"DownloadThread. {0}. url:{1}, path:{2}".format( e, self.url, self.file ) )
            if newfile != None and self.storage.exists( newfile ):
                self.storage.remove( newfile )


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
        newfile = None
        try:
            from limited.files.storage import FilePath
            newfile = self.file + u".part"
            self.storage.zip( self.path, newfile )
            self.storage.rename( newfile, FilePath.name( self.file ) )
        except Exception as e:
            logger.error( u"ZipThread. {0}. path:{1}, zipfile:{2}".format( e, self.path, self.file ) )
            if newfile != None and self.storage.exists( newfile ):
                self.storage.remove( newfile )