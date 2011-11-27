# -*- coding: utf-8 -*-

from limited import settings
from limited.files.storage import FileStorage, FilePath, FileError, FileNotExist

class FileStorageApi: #( FileStorage ):
    """
    Is is a more safety proxy for :class:`~limited.files.storage.FileStorage`.
    It check path to make chroot and other tings.

    Plus hash method.
    """
    xdict = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, lib ):
        self.fs = FileStorage( lib )

    def homepath(self, path):
        path = self.check( path )
        return self.fs.homepath( path )

    def open(self, path, mode='rb', signal=True):
        path = self.check( path )
        return self.fs.open( path, mode, signal )

    def check(self, path):
        """
        Return norm path or raise FileError
        if path is hidden raise FileNotExist
        """
        path = FilePath.norm( path )
        if FilePath.check( path ) == False:
            raise FileError( u"IOError, Permission denied" )
        #TODO: TRASH and CACHE are visible, is is not good.
        if path.startswith( u'.' ) or u'/.' in path:
            if settings.LIMITED_TRASH_PATH not in path and settings.LIMITED_CACHE_PATH not in path:
                raise FileNotExist( u"path '%s' doesn't exist or it isn't a directory" % path )
        return path

    def listdir(self, path, hidden=False):
        """
        Add hashes for all file names.
        """
        path = self.check( path )
        files = self.fs.listdir( path, hidden )
        for file in files:
            name = file['name']
            file['hash'] = self.hash( name )
        return files

    def listTrash(self):
        """
        Safe call for list trash files
        """
        if not self.fs.exists( settings.LIMITED_TRASH_PATH ):
            self.fs.mkdir( settings.LIMITED_TRASH_PATH )
        return self.fs.listdir( settings.LIMITED_TRASH_PATH, hidden=False )

    def exists(self, path):
        path = self.check( path )
        return self.fs.exists( path )

    def size(self, path, dir=False, cached=True):
        path = self.check( path )
        return self.fs.size( path, dir, cached )

    def mkdir(self, path):
        path = self.check( path )
        self.fs.mkdir( path )

    def isfile(self, path):
        path = self.check( path )
        return self.fs.isfile( path )

    def isdir(self, path):
        path = self.check( path )
        return self.fs.isdir( path )

    def move(self, src, dst, signal=True):
        src = self.check( src )
        dst = self.check( dst )
        self.fs.move( src, dst, signal )

    def totrash(self, path, signal=True):
        path = self.check( path )
        self.fs.totrash( path, signal )

    def download(self, url, path, signal=True):
        path = self.check( path )
        self.fs.download( url, path, signal )

    def zip(self, path, file=None, signal=False):
        path = self.check( path )
        self.fs.zip( path, file, signal )

    def unzip(self, path, signal=False):
        path = self.check( path )
        self.fs.unzip( path, signal )

    def rename(self, path, name, signal=True ):
        path = self.check( path )
        self.fs.rename( path, name, signal )

    def save(self, path, file, override=True, signal=True):
        path = self.check( path )
        return self.fs.save( path, file, override=override, signal=signal )

    def remove(self, path, signal=True):
        path = self.check( path )
        self.fs.remove( path, signal )

    def clear(self, path, older=None, signal=True ):
        path = self.check( path )
        self.fs.clear(path, older=older, signal=signal )

    @staticmethod
    def hash(name):
        """
        Return unic hash name for the file name.
        Consists of 3 upper and lower cases letters and numbers.
        """
        xlen = len( FileStorageApi.xdict )
        id = abs( hash( name ) )
        max = xlen ** 3

        while id > max:
            id = id >> 2

        value = ""
        while id != 0:
            remainder = id % xlen
            value += FileStorageApi.xdict[remainder]
            id = id / xlen
        return value