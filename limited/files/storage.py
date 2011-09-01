# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from hashlib import md5
import logging
import os
import shutil
import urllib
import zipfile

from django.core.cache import cache
from django.core.files.base import File
from django.utils.encoding import smart_str, iri_to_uri
from django.utils.http import urlquote

from limited.files.utils import DownloadThread

logger = logging.getLogger(__name__)

class FileError( Exception ):
    """
    File Storage Error
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
    def norm( root, src ):
        """
        If src include '../' or './'
          join root and src and normalise it
        Else return src
        """
        if src.find( '../' ) != -1 or src.find( './' ) != -1:
            path = FilePath.join( root, src )
            path = os.path.normpath( path )
        else:
            path = src

        # delete first '/'
        if path[0] == '/':
            path = path[1:]
        return path


class FileStorage( object ):
    def __init__(self, root, home=u''  ):
        self.root = root
        self.home = home

    def open(self, name, mode='rb'):
        return File( open( self.abspath( name ), mode ) )

    def create(self, name, content):
        name = self.available_name( name )
        
        newfile = self.open( name, 'wb' )
        newfile.write( content )
        newfile.close( )

    def save(self, name, file):
        """
        Save to disk open ``django.core.files.base.File`` object
        also you need to close it yourself
        """
        name = self.available_name( name )

        newfile = self.open( name, 'wb' )
        for chunk in file.chunks( ):
            newfile.write( chunk )

        newfile.close( )

    def download(self, url, path):
        """
        Download file from url
        """
        path = self.available_name( path )
        newfile = path + u".part"
        try:
            # simple hook to stop File proxy access field 'name'
            # that is no exists
            data = urllib.urlopen( iri_to_uri( url ) )
            data.size = int( data.info( )['Content-Length'] )

            self.save( newfile, File( data ) )
            self.rename( newfile, FilePath.name( path ) )
        except Exception:
            if self.exists( newfile ):
                self.remove( newfile )
            raise

    def mkdir(self, name):
        if self.exists( name ):
            raise FileError( u"Directory '%s' already exists" % name )
        os.mkdir( self.abspath( name ) )

    def abspath(self, name):
        return FilePath.join( self.root, name )

    def homepath(self, name):
        return FilePath.join( self.home, name )

    def remove(self, name):
        if not self.exists( name ):
            raise FileNotExist( u"'%s' not found" % name )
        if self.isdir( name ):
            shutil.rmtree( self.abspath( name ) )
        else:
            os.remove( self.abspath( name ) )

    def clear(self, name, older=None):
        """
        Remove all files and dirs in namme directory.
        
        ``older`` needs seconds,
        only top sub dirs checked
        """
        if not self.exists( name ):
            raise FileNotExist( u"'%s' not found" % name )
        if not self.isdir( name ):
            raise FileError( u"'%s' not directory" % name )
        if older == None:
            for item in os.listdir( self.abspath( name ) ):
                file = FilePath.join( name, item )
                self.remove( file )
        else:
            for item in os.listdir( self.abspath( name ) ):
                file = FilePath.join( name, item )
                chenaged = self.created_time( file )
                if datetime.now( ) - chenaged > timedelta( seconds=older ):
                    self.remove( file )

    def move(self, src, dst):
        src_dir = FilePath.dirname( src )
        if src == dst or src_dir == dst:
            raise FileError( u"Moving to the same directory" )
        if not self.exists( src ):
            raise FileNotExist( u"'%s' not found" % src )
        if not self.exists( dst ):
            raise FileNotExist( u"'%s' not found" % dst )

        name = FilePath.name( src )

        dst = FilePath.join( dst, name )
        dst = self.available_name( dst )
        shutil.move( self.abspath( src ), self.abspath( dst ) )

    def rename(self, path, name):
        if '/' in name:
            raise FileError( u"'%s' contains not supported symbols" % name )
        if not self.exists( path ):
            raise FileNotExist( u"'%s' not found" % path )
        new_path = FilePath.join( FilePath.dirname( path ), name )
        if self.exists( new_path ):
            raise FileError( u"'%s' already exist!" % name )
        os.rename( self.abspath( path ), self.abspath( new_path ) )

    def totrash(self, name):
        if not self.exists( name ):
            raise FileNotExist( u"%s not found" % name )
        if not self.exists( u".TrashBin" ):
            self.mkdir( u".TrashBin"  )
        self.move( name, u".TrashBin"  )

    def exists(self, name):
        return os.path.exists( self.abspath( name ) )

    def isfile(self, name):
        return os.path.isfile( self.abspath( name ) )

    def isdir(self, name):
        return os.path.isdir( self.abspath( name ) )

    def listdir(self, path, hidden=False):
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
                    'size': self.size( fullpath ),
                    'time': self.modified_time( fullpath ),
                    } )

        files = sorted( files, key=lambda strut: strut['name'] )
        files = sorted( files, key=lambda strut: strut['class'] )
        return files

    def listfiles(self, path, hidden=False ):
        """
        List files recursive
        Return dict { abspath : path from root }
        """
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
        return dir and files size
        if dir, size will be sum recursive else 0
        if cached, dirs size will be cached
        """
        if self.isfile( self.abspath( name ) ):
            return os.path.getsize( self.abspath( name ) )

        if dir and self.isdir( self.abspath( name ) ):
            key = md5( "storage.size" + smart_str( name ) ).hexdigest( )
            size = cache.get( key ) or 0
            if size:
                return size

            for item in os.listdir( self.abspath( name ) ):
                file = FilePath.join( name, item )
                size += self.size( file, dir=True )

            if cached: cache.set( key, size, 120 )
            return size
        return 0

    def zip(self, path, file=None ):
        """
        zip file or directory `path` to `file` or to `path`.zip if file=None
        """
        if file == None:
            file = self.available_name( path + u".zip" )

        newfile = file + u".part"
        try:
            zfile = self.open( newfile, mode='wb' )
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
            self.rename( newfile, FilePath.name( file ) )
        except Exception:
            if self.exists( newfile ):
                self.remove( newfile )
            raise

    def unzip(self, path ):
        file = self.abspath( path )
        zip = zipfile.ZipFile( file )
        # To lazy to do converting
        # maybe chardet help later
        try:
            zip.extractall( FilePath.dirname( file ) )
        except UnicodeDecodeError as e:
            raise FileError( u"Unicode decode error, try unzip yourself" )

    def url(self, name):
        return urlquote(name)

    def available_name(self, path):
        # if file exists add [i] to file name
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
        return datetime.fromtimestamp( os.path.getatime( self.abspath( name ) ) )

    def created_time(self, name):
        return datetime.fromtimestamp( os.path.getctime( self.abspath( name ) ) )

    def modified_time(self, name):
        return datetime.fromtimestamp( os.path.getmtime( self.abspath( name ) ) )
