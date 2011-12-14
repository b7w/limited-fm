# -*- coding: utf-8 -*-
import re

from limited.files.utils import FilePath
from limited.files.api.base import file_pre_change, FileStorageBaseApi
from limited.files.api.extra import FileStorageExtra
from limited.files.api.trash import FileStorageTrash
from limited.files.storage import FileError, FileNotExist

class FileStorageApi( FileStorageBaseApi ):
    """
    Height level api for :class:`~limited.files.storage.FileStorage`.
    It check path to make chroot and other tings.

    Have ``trash`` and ``extra`` fields with :class:`limited.files.api.FileStorageTrash` and
    :class:`limited.files.api.FileStorageExtra` objects
    """
    re_mkdir = re.compile( r"([/\.\(\)\[\]\w -]*)" )

    def __init__(self, lib):
        """
        Take :class:`limited.models.FileLib` as a parameter
        """
        FileStorageBaseApi.__init__( self, lib )
        self.trash = FileStorageTrash( lib )
        self.extra = FileStorageExtra( lib )

    def open(self, path, mode='rb', signal=True):
        """
        Return open django :class:`~django.core.files.base.File` instance
        """
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        path = self.check( path )
        return self.fs.open( path, mode )

    def listdir(self, path, hidden=False):
        """
        Return list of files in directory.
        Each item is a dict with class:'file'|'dir', name: file name, url - url encode path,
        size: file size, time: modified_time.
        If ``hidden`` ``True`` than hidden files will be include.
        Data sorted first by name and than by directory.
        On not dir exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        path = self.check( path )
        files = self.fs.listdir( path, hidden )
        for file in files:
            name = file['name']
            file['hash'] = self.hash( name )
        return files

    def exists(self, path):
        """
        Return ``True`` if file exists or ``False``
        """
        path = self.check( path )
        return self.fs.exists( path )

    def size(self, path, dir=False, cached=True):
        """
        Return dir and files size. If ``dir`` ``True``, size will be sum recursive else return 0
        if ``cached``, dirs size will be cached.
        On not exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        path = self.check( path )
        return self.fs.size( path, dir, cached )

    def mkdir(self, path):
        """
        Create directory, on exist raise :class:`~limited.files.storage.FileError`
        """
        path = self.check( path )
        flag = FileStorageApi.re_mkdir.match( path )
        if flag == None:
            raise FileError( u"Not supported symbols" )
        elif flag.group(0) != path:
            raise FileError( u"Not supported symbols" )

        if self.exists( path ) == True:
            raise FileError( u"Directory '%s' already exists" % path )
        self.fs.mkdir( path )

    def isfile(self, path):
        """
        Return ``True`` if it is a file or ``False``
        """
        path = self.check( path )
        return self.fs.isfile( path )

    def isdir(self, path):
        """
        Return ``True`` if it is a directory or ``False``
        """
        path = self.check( path )
        return self.fs.isdir( path )

    def move(self, src, dst, signal=True):
        """
        Move file or dir from ``src`` to ``dst``.
        On the same directory raise :class:`~limited.files.storage.FileError`.
        On not exist for both paths raise :class:`~limited.files.storage.FileNotExist`.
        """
        src_dir = FilePath.dirname( src )
        if src == dst or src_dir == dst:
            raise FileError( u"Moving to the same directory" )
        if self.exists( src ) == False:
            raise FileNotExist( u"'%s' not found" % src )
        if self.exists( dst ) == False:
            raise FileNotExist( u"'%s' not found" % dst )
        src = self.check( src )
        dst = self.check( dst )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( src ) )
            file_pre_change.send( self, basedir=dst )
        self.fs.move( src, dst )

    def rename(self, path, name, signal=True ):
        """
        Rename file or dir path ``path`` to name ``name``.
        On '/' in ``name`` raise :class:`~limited.files.storage.FileError`.
        On not exist or already exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        path = self.check( path )
        if '/' in name:
            raise FileError( u"'%s' contains not supported symbols" % name )
        if self.exists( path ) == False:
            raise FileNotExist( u"'%s' not found" % path )

        new_path = FilePath.join( FilePath.dirname( path ), name )
        if self.exists( new_path ):
            raise FileError( u"'%s' already exist!" % name )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        self.fs.rename( path, name )

    def save(self, path, file, override=True, signal=True):
        """
        Return path to the file, that can be another from ``path``.
        Copy to disk to ``path`` open :class:`~django.core.files.base.File` object ``file``.
        Also you need to close it yourself.
        """
        path = self.check( path )
        path = self.available_name( path, override )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        return self.fs.save( path, file )

    def remove(self, path, signal=True):
        """
        Remove directory or file, on not exist raise :class:`~limited.files.storage.FileNotExist`
        """
        path = self.check( path )
        if self.exists( path ) == False:
            raise FileNotExist( u"'%s' not found" % path )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        self.fs.remove( path )

    def time(self, path, type=u"modified" ):
        """
        Return type = accessed|created|modified time or raise error if not match
        """
        if type == u"accessed":
            return self.fs.accessed_time( path )
        if type == u"created":
            return self.fs.created_time( path )
        if type == u"modified":
            return self.fs.modified_time( path )
        raise FileError( u"Wrong time type name '%s'" % type )