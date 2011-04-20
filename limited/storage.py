# -*- coding: utf-8 -*-

from datetime import datetime
import logging
from hashlib import md5
import os
import shutil
import threading
import urllib
import zipfile
from django.core.cache import cache
from django.utils.encoding import smart_str

from django.utils.log import logger

class StorageError( Exception ):
    pass


class StoragePath( object ):
    def join(self, path, name ):
        return os.path.join( path, name )

    def name(self, path):
        return os.path.basename( path )

    def dirname(self, path):
        return os.path.dirname( path )

    # If src include '../' or './'
    #  join root and src and normalise it
    # Else return src
    def norm(self, root, src ):
        if src.find( '../' ) != -1 or src.find( './' ) != -1:
            path = self.join( root, src )
            path = os.path.normpath( path )
            if path.find( '../' ) != -1 or path.find( './' ) != -1:
                raise StorageError( "Wrong path '%s'" % path )
        else:
            path = src

        # delete first '/'
        if path[0] == '/':
            path = path[1:]
        return path

# List files recursive
# Return dict { abspath : path from root }
def ListFiles( root, dir='', array={ } ):
    absdir = os.path.join( root, dir )
    for name in os.listdir( absdir ):
        fullpath = os.path.join( absdir, name )
        if os.path.isdir( fullpath ):
            dirpath = os.path.join( dir, name )
            array = ListDir( root, dirpath, array )

        if os.path.isfile( fullpath ):
            path = os.path.join( dir, name )
            array[fullpath] = path

    return array

# Download file from url in a thread.
# So big files can be download without stopping django process
# While downloading, file has name '[Download]{Name}'
class DowloadThread( threading.Thread ):
    def __init__(self, url, file, *args, **kwargs):
        super( DowloadThread, self ).__init__( *args, **kwargs )
        self.url = url
        self.file = file

    def run(self):
        try:
            path, name = os.path.split( self.file )
            file = os.path.join( path, '[Download]'+name )
            urllib.urlretrieve( self.url, file )
            os.rename( file, self.file )
        except Exception:
            if os.path.exists( self.file ):
                os.remove( self.file )


class FileStorage( object ):
    def __init__(self, home ):
        self.home = home
        self.path = StoragePath( )

    def open(self, name, mode='rb'):
        return open( self.abspath( name ), mode )

    def save(self, name, file):
        name = self.available_name( name )

        newfile = open( self.abspath( name ), 'wb' )
        for chunk in file.chunks( ):
            newfile.write( chunk )

        newfile.close( )

    def download(self, path, url):
        name = self.path.name( url )
        file = self.path.join( self.abspath( path ), name )
        thread = DowloadThread( url, file )
        thread.start( );

    def mkdir(self, name):
        if self.exists( name ):
            raise StorageError( "Directory '%s' already exists" % name )
        os.mkdir( self.abspath( name ) )

    def abspath(self, name):
        return self.path.join( self.home, name )

    def delete(self, name):
        os.remove( self.abspath( name ) )

    def move(self, src, dst):
        src_dir = self.path.dirname( src )
        if src_dir == dst:
            raise StorageError( "Moving to the same directory" )
        if not self.exists( src ):
            raise StorageError( "'%s' not found" % src )
        if not self.exists( dst ):
            raise StorageError( "'%s' not found" % dst )

        name = self.path.name( src )

        dst = self.path.join( dst, name )
        dst = self.available_name( dst )
        shutil.move( self.abspath( src ), self.abspath( dst ) )

    def rename(self, path, name):
        if '/' in name:
            raise StorageError( "'%s' contains not supported symbols" % name )
        if not self.exists( path ):
            raise StorageError( "'%s' not found" % path )
        new_path = self.path.join( self.path.dirname( path ), name )
        if self.exists( new_path ):
            raise StorageError( u"'%s' already exist!" % name )
        os.rename( self.abspath( path ), self.abspath( new_path ) )

    def totrash(self, name):
        if not self.exists( name ):
            raise StorageError( '%s not found' % name )
        if not self.exists( '.TrashBin' ):
            self.mkdir( '.TrashBin' )
        self.move( name, '.TrashBin' )

    def exists(self, name):
        return os.path.exists( self.abspath( name ) )

    def isfile(self, name):
        return os.path.isfile( self.abspath( name ) )

    def isdir(self, name):
        return os.path.isdir( self.abspath( name ) )

    def listdir(self, path, hidden=False):
        if not (self.exists( path ) and self.isdir( path ) ):
            raise StorageError( "path '%s' doesn't exist or it isn't a directory" % path )

        tmp = os.listdir( self.abspath( path ) )
        files = []
        if not hidden:
            tmp = filter( lambda x: x.startswith( '.' ) == 0, tmp )

        for item in tmp:
            fullpath = self.path.join( path, item )
            if self.isfile( fullpath ): ccl = 'file'
            if self.isdir( fullpath ): ccl = 'dir'

            files.append(
                    {
                    'class': ccl,
                    'name': item,
                    'url': self.url( fullpath ),
                    'size': self.size( fullpath ),
                    'time': self.created_time( fullpath ),
                    } )

        files = sorted( files, key=lambda strut: strut['name'] )
        files = sorted( files, key=lambda strut: strut['class'] )
        return files

    # List files recursive
    # Return dict { abspath : path from root }
    def listfiles(self, path, dir='', array={ } ):
        root = self.abspath( path )
        absdir = os.path.join( root, dir )
        for name in os.listdir( absdir ):
            fullpath = os.path.join( absdir, name )
            if os.path.isdir( fullpath ):
                dirpath = os.path.join( dir, name )
                array = self.listfiles( path, dirpath, array )

            if os.path.isfile( fullpath ):
                fullname = os.path.join( dir, name )
                array[fullpath] = fullname

        return array

    # return dir and files size
    def size(self, name, dir=False, cached=True):

        if self.isfile( self.abspath( name ) ):
            return os.path.getsize( self.abspath( name ) )

        if dir and self.isdir( self.abspath( name ) ):
            key = md5( smart_str( name ) ).hexdigest( )
            size = cache.get( key ) or 0
            if size : return size

            for item in os.listdir( self.abspath( name ) ):
                file = self.path.join( name, item )
                size += self.size( file, dir=True )

            if cached: cache.set(key, size, 120)
            return size
        return 0

    def zip(self, path ):
        file = self.abspath( path ) + '.zip'
        file = self.available_name( file )
        temp = open( file, mode='w' )
        archive = zipfile.ZipFile( temp, 'w', zipfile.ZIP_DEFLATED )
        if self.isdir( path ):
            dirname = self.path.name( path )
            for abspath, name in self.listfiles( path ).items( ):
                name = self.path.join( dirname, name )
                archive.write( abspath, name )
        if self.isfile( path ):
            archive.write( self.abspath( path ), self.path.name( path ) )

        archive.close( )
        temp.seek( 0 )

    def unzip(self, path ):
        file = self.abspath( path )
        zip = zipfile.ZipFile( file )
        zip.extractall( self.path.dirname( file ) )

    def url(self, name):
        return name

    def available_name(self, path):
        # if file exists add [i] to file name
        file, ext = os.path.splitext( path )
        i = 1
        while i != 0:
            if self.exists( self.abspath( path ) ):
                path = file + '[' + str( i ) + ']' + ext
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
