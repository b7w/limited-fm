# -*- coding: utf-8 -*-

from limited.files.api.base import file_pre_change, FileStorageBaseApi
from limited.files.api.extra import FileStorageExtra
from limited.files.api.trash import FileStorageTrash
from limited.files.storage import FileError, FileNotExist, FilePath

class FileStorageApi( FileStorageBaseApi ):
    """
    Is is a more safety proxy for :class:`~limited.files.storage.FileStorage`.
    It check path to make chroot and other tings.

    Plus hash method.
    """

    def __init__(self, lib):
        FileStorageBaseApi.__init__( self, lib )
        self.trash = FileStorageTrash( lib )
        self.extra = FileStorageExtra( lib )

    def open(self, path, mode='rb', signal=True):
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        path = self.check( path )
        return self.fs.open( path, mode )

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

    def exists(self, path):
        path = self.check( path )
        return self.fs.exists( path )

    def size(self, path, dir=False, cached=True):
        path = self.check( path )
        return self.fs.size( path, dir, cached )

    def mkdir(self, path):
        path = self.check( path )
        if self.exists( path ) == True:
            raise FileError( u"Directory '%s' already exists" % path )
        self.fs.mkdir( path )

    def isfile(self, path):
        path = self.check( path )
        return self.fs.isfile( path )

    def isdir(self, path):
        path = self.check( path )
        return self.fs.isdir( path )

    def move(self, src, dst, signal=True):
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
        path = self.check( path )
        path = self.available_name( path, override )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        return self.fs.save( path, file )

    def remove(self, path, signal=True):
        path = self.check( path )
        if self.exists( path ) == False:
            raise FileNotExist( u"'%s' not found" % path )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        self.fs.remove( path )

    def time(self, path, type=u"modified" ):
        if type == u"accessed":
            return self.fs.accessed_time( path )
        if type == u"created":
            return self.fs.created_time( path )
        if type == u"modified":
            return self.fs.modified_time( path )
        raise FileError( u"Wrong time type name '%s'" % type )