# -*- coding: utf-8 -*-

from django.dispatch.dispatcher import Signal

from limited import settings
from limited.files.storage import FileNotExist, FileStorage, FilePath, FileError

# Signal before file change
# basedir - dir in witch file or dir changed
# Main idea of signal to stop zipping dir or delete cache
# Signal sent in ``open```( create, save ), ``remove``( clear, totrash ), ``zip``
file_pre_change = Signal( providing_args=["basedir"] )



class FileStorageBaseApi:
    """
    It is a abstract class for Files storage Api.
    It have some useful static methods like url,available_name and etc
    """
    xdict = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, lib ):
        """
        Take :class:`limited.models.FileLib` as a parameter
        """
        self.lib = lib
        self.fs = FileStorage( lib )

    @staticmethod
    def check(path):
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

    @staticmethod
    def hash(name):
        """
        Return unic hash name for the file name.
        Consists of 3 upper and lower cases letters and numbers.
        """
        xlen = len( FileStorageBaseApi.xdict )
        id = abs( hash( name ) )
        max = xlen ** 3

        while id > max:
            id = id >> 2

        value = ""
        while id != 0:
            remainder = id % xlen
            value += FileStorageBaseApi.xdict[remainder]
            id = id / xlen
        return value

    def homepath(self, path):
        """
        Return path from :ref:`LIMITED_ROOT_PATH <SETTINGS_ROOT_PATH>`
        """
        path = self.check( path )
        return FilePath.join( self.lib.path, path )

    def available_name(self, path, override=False):
        """
        Return available file path.
        If file exists add '[i]' to file name.
        If overrideTrue - override, False - create new name, Else - raise FileError
        """
        if self.fs.exists( path ) == True:
            if override == True:
                return path
            elif override == False:
                return self.fs.available_name( path )
            else:
                raise FileError( u"'%s' exists" % path )
        return path

    def url(self, path):
        """
        Return urlquote path name
        """
        path = self.check( path )
        return self.fs.url( path )