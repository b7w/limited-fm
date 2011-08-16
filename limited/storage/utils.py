# -*- coding: utf-8 -*-

import logging
import os
import threading
import urllib

logger = logging.getLogger( __name__ )

class DownloadThread( threading.Thread ):
    """
    Download file in a thread
    """

    def __init__(self, url, file, *args, **kwargs ):
        super( DownloadThread, self ).__init__( *args, **kwargs )
        self.url = url
        self.file = file

    def run(self):
        try:
            path, name = os.path.split( self.file )
            newfile = os.path.join( path, u"[Downloading]" + name )
            urllib.urlretrieve( self.url, newfile )
            os.rename( newfile, self.file )
        except Exception as e:
            logger.error( u"DownloadThread. {0}. url:{1}, path:{2}".format( e, self.url, self.file ) )
            if os.path.exists( self.file ):
                os.remove( self.file )


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
            tmp = self.file + u".part"
            self.storage.zip( self.path, tmp )
            self.storage.rename( tmp, self.storage.path.name( self.file ) )
        except Exception as e:
            logger.error( e )