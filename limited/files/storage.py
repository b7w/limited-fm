# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from hashlib import md5
import os
import shutil
import urllib
import zipfile
import errno

from django.core.cache import cache
from django.core.files.base import File
from django.dispatch import Signal
from django.utils.encoding import smart_str, iri_to_uri
from django.utils.http import urlquote

from limited import settings


# Signal before file change
# basedir - dir in witch file or dir changed
# Main idea of signal to stop zipping dir or delete cache
# Signal sent in ``open```( create, save ), ``remove``( clear, totrash ), ``zip``
file_pre_change = Signal( providing_args=["basedir"] )

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


class FilePath( object ):
    @staticmethod
    def join( path, name ):
        """
        join to path, if ``mane`` start with '/'
        return ``name``
        """
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
        return os.path.normpath( path )

    @staticmethod
    def split( path ):
        """
        Split path
        """
        if len(path) > 1 and path[0] == '/':
            path = path[1:]
        if len(path) > 1 and path[-1] == '/':
            path = path[:-1]
        return path.split( '/' )


class FileStorage( object ):
    def __init__(self, lib ):
        self.lib = lib
        self.root = lib.get_path()
        self.home = lib.path

    def open(self, name, mode='rb', signal=True ):
        """
        Return open django :class:`~django.core.files.base.File` instance
        """
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( name ) )
        try:
            return File( open( self.abspath( name ), mode ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, open. Permission denied '%s'" % name )

    def create(self, name, content, signal=True ):
        """
        Write to file ``name`` same data ``content``
        """
        name = self.available_name( name )
        
        newfile = self.open( name, 'wb', signal=signal )
        newfile.write( content )
        newfile.close( )

    def save(self, name, file, signal=True ):
        """
        Copy to disk to ``name`` open :class:`~django.core.files.base.File` object ``file``.
        Also you need to close it yourself.
        """
        name = self.available_name( name )

        newfile = self.open( name, 'wb', signal=signal )
        for chunk in file.chunks( ):
            newfile.write( chunk )

        newfile.close( )

    def download(self, url, path, signal=True ):
        """
        Download file from ``url`` to file ``path``.
        The process goes to a file ``path + '.part'``.
        On error file will be remove.
        To get file name from url use :class:`~limited.utils.url_get_filename`.
        """
        path = self.available_name( path )
        newfile = path + u".part"
        try:
            # simple hook to stop File proxy access field 'name'
            # that is no exists
            if signal:
                file_pre_change.send( self, basedir=FilePath.dirname( path ) )
            data = urllib.urlopen( iri_to_uri( url ) )
            data.size = int( data.info( )['Content-Length'] )
            self.save( newfile, File( data ), signal=False  )
            self.rename( newfile, FilePath.name( path ), signal=False )
        except Exception:
            if self.exists( newfile ):
                self.remove( newfile, signal=False  )
            raise

    def mkdir(self, name):
        """
        Create directory, on exist raise :class:`~limited.files.storage.FileError`
        """
        if self.exists( name ):
            raise FileError( u"Directory '%s' already exists" % name )
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

    def homepath(self, name):
        """
        Return path from :ref:`LIMITED_ROOT_PATH <SETTINGS_ROOT_PATH>`
        """
        return FilePath.join( self.home, name )

    def remove(self, name, signal=True ):
        """
        Remove directory or file, on not exist raise :class:`~limited.files.storage.FileNotExist`
        """
        if not self.exists( name ):
            raise FileNotExist( u"'%s' not found" % name )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( name ) )
        try:
            if self.isdir( name ):
                shutil.rmtree( self.abspath( name ) )
            else:
                os.remove( self.abspath( name ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, remove. Permission denied '%s'" % name )

    def clear(self, name, older=None, signal=True ):
        """
        Remove all files and dirs in ``name`` directory.
        ``older`` takes seconds for max age from created_time, only top sub dirs checked.
        On not exist raise :class:`~limited.files.storage.FileNotExist`.
        On not directory raise :class:`~limited.files.storage.FileError`.
        """
        if not self.exists( name ):
            raise FileNotExist( u"'%s' not found" % name )
        if not self.isdir( name ):
            raise FileError( u"'%s' not directory" % name )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( name ) )
        if older == None:
            for item in os.listdir( self.abspath( name ) ):
                file = FilePath.join( name, item )
                self.remove( file, signal=False )
        else:
            for item in os.listdir( self.abspath( name ) ):
                file = FilePath.join( name, item )
                chenaged = self.created_time( file )
                if datetime.now( ) - chenaged > timedelta( seconds=older ):
                    self.remove( file, signal=False )

    def move(self, src, dst, signal=True ):
        """
        Move file or dir from ``src`` to ``dst``.
        On the same directory raise :class:`~limited.files.storage.FileError`.
        On not exist for both paths raise :class:`~limited.files.storage.FileNotExist`.
        """
        src_dir = FilePath.dirname( src )
        if src == dst or src_dir == dst:
            raise FileError( u"Moving to the same directory" )
        if not self.exists( src ):
            raise FileNotExist( u"'%s' not found" % src )
        if not self.exists( dst ):
            raise FileNotExist( u"'%s' not found" % dst )

        name = FilePath.name( src )

        # send signal to source src and dst
        if signal:
            file_pre_change.send( self, basedir=src_dir )
            file_pre_change.send( self, basedir=dst )

        dst = FilePath.join( dst, name )
        dst = self.available_name( dst )
        try:
            shutil.move( self.abspath( src ), self.abspath( dst ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, move. Permission denied '%s'" % src )

    def rename(self, path, name, signal=True ):
        """
        Rename file or dir path ``path`` to name ``name``.
        On '/' in ``name`` raise :class:`~limited.files.storage.FileError`.
        On not exist or already exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        if '/' in name:
            raise FileError( u"'%s' contains not supported symbols" % name )
        if not self.exists( path ):
            raise FileNotExist( u"'%s' not found" % path )
        new_path = FilePath.join( FilePath.dirname( path ), name )
        if self.exists( new_path ):
            raise FileError( u"'%s' already exist!" % name )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        try:
            os.rename( self.abspath( path ), self.abspath( new_path ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, rename. Permission denied '%s'" % path )

    def totrash(self, name, signal=True ):
        """
        Shortcut for :func:`~limited.files.storage.FileStorage.move`
        where second var is :ref:`LIMITED_TRASH_PATH <SETTINGS_TRASH_PATH>`.
        """
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( name ) )
        if not self.exists( settings.LIMITED_TRASH_PATH ):
            self.mkdir( settings.LIMITED_TRASH_PATH  )
        self.move( name, settings.LIMITED_TRASH_PATH, signal=False )

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

    def listdir(self, path, hidden=False):
        """
        Return list of files in directory.
        Each item is a dict with class:'file'|'dir', name: file name, url - url encode path,
        size: file size, time: modified_time.
        If ``hidden`` ``True`` than hidden files will be include.
        Data sorted first by name and than by directory.
        On not dir exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        if not (self.exists( path ) and self.isdir( path ) ):
            raise FileNotExist( u"path '%s' doesn't exist or it isn't a directory" % path )

        tmp = os.listdir( self.abspath( path ) )
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
                    'hash': self.hash( item ),
                    'size': self.size( fullpath ),
                    'time': self.modified_time( fullpath ),
                    } )

        files = sorted( files, key=lambda strut: strut['name'] )
        files = sorted( files, key=lambda strut: strut['class'] )
        return files

    def listfiles(self, path, hidden=False ):
        """
        List files recursive.
        Return dict ``{ abspath : path from root, }``.
        If ``hidden`` ``True`` than hidden files will be include.
        On not dir exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        if not (self.exists( path ) and self.isdir( path ) ):
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

        return _listfiles( path, "", {}, hidden=hidden )

    def size(self, name, dir=False, cached=True):
        """
        Return dir and files size. If ``dir`` ``True``, size will be sum recursive else return 0
        if ``cached``, dirs size will be cached.
        On not exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        if not self.exists( name ):
            raise FileNotExist( u"'%s' not found" % name )

        if self.isfile( self.abspath( name ) ):
            return os.path.getsize( self.abspath( name ) )

        if dir and self.isdir( self.abspath( name ) ):
            key = md5( "storage.size" + smart_str( name ) ).hexdigest( )
            if cached == True:
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

    def zip(self, path, file=None, signal=False ):
        """
        Zip file or directory ``path`` to ``file`` or to ``path + '.zip'``.
        On not exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        if not self.exists( path ):
            raise FileNotExist( u"'%s' not found" % path )

        if file == None:
            file = self.available_name( path + u".zip" )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )

        newfile = file + u".part"
        try:
            zfile = self.open( newfile, mode='wb', signal=False )
            archive = zipfile.ZipFile( zfile, 'w', zipfile.ZIP_DEFLATED )
            if self.isdir( path ):
                dirname = FilePath.name( path )
                for abspath, name in self.listfiles( path ).items( ):
                    name = FilePath.join( dirname, name )
                    archive.write( abspath, name )
            elif self.isfile( path ):
                archive.write( self.abspath( path ), FilePath.name( path ) )

            archive.close( )
            zfile.seek( 0 )
            self.rename( newfile, FilePath.name( file ), signal=False )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, zip. Permission denied '%s'" % name )
        finally:
            if self.exists( newfile ):
                self.remove( newfile, signal=False )

    def unzip(self, path, signal=False ):
        """
        Unzip file or directory ``path``.
        On not exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        if not self.exists( path ):
            raise FileNotExist( u"'%s' not found" % path )

        file = self.abspath( path )
        zip = zipfile.ZipFile( file )
        # To lazy to do converting
        # maybe chardet help later
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        try:
            zip.extractall( FilePath.dirname( file ) )
        except UnicodeDecodeError as e:
            raise FileError( u"Unicode decode error, try unzip yourself" )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, unzip. Permission denied '%s'" % path )

    def url(self, name):
        """
        Return urlquote path name
        """
        return urlquote(name)

    @staticmethod
    def hash(name):
        """
        Return unic hash name for the file name.
        Consists of 3 upper and lower cases letters and numbers.
        """
        id = abs( hash( name ) ) >> 8
        xdict = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        xlen = len( xdict )
        value = ""
        while id >= xlen:
            id = id / xlen
            remainder = id % xlen
            value += xdict[remainder]
        return value

    def available_name(self, path):
        """
        Return available file path.
        If file exists add '[i]' to file name.
        """
        file, ext = os.path.splitext( path )
        i = 1
        while i != 0:
            if self.exists( self.abspath( path ) ):
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