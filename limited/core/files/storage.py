# -*- coding: utf-8 -*-

from datetime import datetime
from hashlib import md5
import os
import shutil
import errno

from django.core.cache import cache
from django.core.files.base import File
from django.utils.encoding import smart_str
from django.utils.http import urlquote

from limited.core.files.utils import FilePath


class FileError( Exception ):
    """
    File Storage Error. Base for all storage errors.
    """
    pass


class FileNotExist( FileError ):
    """
    File not Found Storage Error
    """
    pass


class FileStorage( object ):
    def __init__(self, lib ):
        self.lib = lib
        self.root = lib.get_path( )
        self.home = lib.path

    def open(self, name, mode='rb'):
        """
        Return open django :class:`~django.core.files.base.File` instance
        """
        try:
            return File( open( self.abspath( name ), mode ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, open. Permission denied '%s'" % name )

    def save(self, name, file, signal=True ):
        """
        Return path to the file, that can be another from ``name``.
        Copy to disk to ``name`` open :class:`~django.core.files.base.File` object ``file``.
        Also you need to close it yourself.
        """
        newfile = self.open( name, 'wb' )
        for chunk in file.chunks( ):
            newfile.write( chunk )

        newfile.close( )
        return name

    def mkdir(self, name):
        """
        Create directory, on exist raise :class:`~limited.core.files.storage.FileError`
        """
        try:
            os.mkdir( self.abspath( name ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, mkdir. Permission denied '%s'" % name )

    def abspath(self, name):
        """
        Return absolute filesystem path to file
        """
        return FilePath.join( self.root, name )

    def remove(self, name):
        """
        Remove directory or file, on not exist raise :class:`~limited.core.files.storage.FileNotExist`
        """
        try:
            if self.isdir( name ):
                shutil.rmtree( self.abspath( name ) )
            else:
                os.remove( self.abspath( name ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, remove. Permission denied '%s'" % name )

    def move(self, src, dst ):
        """
        Move file or dir from ``src`` to ``dst``.
        On the same directory raise :class:`~limited.core.files.storage.FileError`.
        On not exist for both paths raise :class:`~limited.core.files.storage.FileNotExist`.
        """
        name = FilePath.name( src )

        dst = FilePath.join( dst, name )
        dst = self.available_name( dst )
        try:
            shutil.move( self.abspath( src ), self.abspath( dst ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, move. Permission denied '%s'" % src )

    def rename(self, path, name ):
        """
        Rename file or dir path ``path`` to name ``name``.
        On '/' in ``name`` raise :class:`~limited.core.files.storage.FileError`.
        On not exist or already exist raise :class:`~limited.core.files.storage.FileNotExist`.
        """
        new_path = FilePath.join( FilePath.dirname( path ), name )
        try:
            os.rename( self.abspath( path ), self.abspath( new_path ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, rename. Permission denied '%s'" % path )

    def exists(self, name):
        """
        Return ``True`` if file exists or ``False``
        """
        return os.path.exists( self.abspath( name ) )

    def isfile(self, name):
        """
        Return ``True`` if it is a file or ``False``
        """
        return os.path.isfile( self.abspath( name ) )

    def isdir(self, name):
        """
        Return ``True`` if it is a directory or ``False``
        """
        return os.path.isdir( self.abspath( name ) )

    def list(self, name):
        """
        Return listi of files in directory
        """
        if not self.isdir(name):
            raise FileNotExist( u"path '%s' doesn't exist or it isn't a directory" % name )
        return os.listdir( self.abspath( name ) )

    def listdir(self, path, hidden=False):
        """
        Return list of files in directory.
        Each item is a dict with class:'file'|'dir', name: file name, url - url encode path,
        size: file size, time: modified_time.
        If ``hidden`` ``True`` than hidden files will be include.
        Data sorted first by name and than by directory.
        On not dir exist raise :class:`~limited.core.files.storage.FileNotExist`.
        """
        tmp = self.list( path )
        files = []
        if not hidden:
            tmp = filter( lambda x: x.startswith( '.' ) == 0, tmp )

        for item in tmp:
            fullpath = FilePath.join( path, item )
            if self.isfile( fullpath ): ccl = 'file'
            if self.isdir( fullpath ): ccl = 'dir'

            files.append(
                    {
                    'class': ccl,
                    'name': item,
                    'url': self.url( fullpath ),
                    'size': self.size( fullpath ),
                    'time': self.modified_time( fullpath ),
                    } )

        files = sorted( files, key=lambda strut: strut['name'] )
        files = sorted( files, key=lambda strut: strut['class'], reverse=False )
        return files

    def listfiles(self, path, hidden=False ):
        """
        List files recursive.
        Return dict ``{ abspath : path from root, }``.
        If ``hidden`` ``True`` than hidden files will be include.
        On not dir exist raise :class:`~limited.core.files.storage.FileNotExist`.
        """
        if not self.isdir( path ):
            raise FileNotExist( u"path '%s' doesn't exist or it isn't a directory" % path )

        def _listfiles( path, dir, array, hidden=False ):
            root = self.abspath( path )
            absdir = os.path.join( root, dir )
            for name in os.listdir( absdir ):
                if not name.startswith( u'.' ):
                    fullpath = os.path.join( absdir, name )
                    if os.path.isdir( fullpath ):
                        dirpath = os.path.join( dir, name )
                        array = _listfiles( path, dirpath, array )

                    if os.path.isfile( fullpath ):
                        fullname = os.path.join( dir, name )
                        array[fullpath] = fullname

            return array

        return _listfiles( path, "", { }, hidden=hidden )

    def size(self, name, dir=False, cached=True):
        """
        Return dir and files size. If ``dir`` ``True``, size will be sum recursive else return 0
        if ``cached``, dirs size will be cached.
        On not exist raise :class:`~limited.core.files.storage.FileNotExist`.
        """
        if not self.exists( name ):
            raise FileNotExist( u"'%s' not found" % name )

        if self.isfile( name ):
            return os.path.getsize( self.abspath( name ) )

        if dir and self.isdir( name ):
            key = md5( "storage.size" + smart_str( name ) ).hexdigest( )
            if cached:
                size = cache.get( key )
                if size != None:
                    return size

            size = 0
            for item in os.listdir( self.abspath( name ) ):
                file = FilePath.join( name, item )
                size += self.size( file, dir=True, cached=cached )

            if cached: cache.set( key, size, 120 )
            return size
        return 0

    def url(self, name):
        """
        Return urlquote path name
        """
        return urlquote( name )

    def available_name(self, path):
        """
        Return available file path.
        If file exists add '[i]' to file name.
        """
        file, ext = os.path.splitext( path )
        i = 1
        while i != 0:
            if self.exists( path ):
                path = file + u'[' + unicode( i ) + u']' + ext
                i += 1
            else:
                i = 0
        return path

    def accessed_time(self, name):
        """
        Return accessed time
        """
        return datetime.fromtimestamp( os.path.getatime( self.abspath( name ) ) )

    def created_time(self, name):
        """
        Return created time
        """
        return datetime.fromtimestamp( os.path.getctime( self.abspath( name ) ) )

    def modified_time(self, name):
        """
        Return modified time
        """
        return datetime.fromtimestamp( os.path.getmtime( self.abspath( name ) ) )