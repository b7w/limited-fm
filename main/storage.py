# -*- coding: utf-8 -*-

from datetime import datetime
import os
import shutil

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
        if src.find('../') != -1 or src.find('./') != -1:
            path = self.join( root, src )
            path = os.path.normpath( path )
            if path.find('../') != -1 or path.find('./') != -1:
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

    def mkdir(self, name):
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

    def size(self, name):
        return os.path.getsize( self.abspath( name ) )

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
