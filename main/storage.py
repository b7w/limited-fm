from datetime import datetime
import os


class StoragePath( object ):
    def join(self, path, name ):
        return os.path.join( path, name )

    def name(self, path):
        return os.path.basename( path )

    def dirname(self, path):
        return os.path.dirname( path )


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
        newfile = open( self.abspath( name ), 'wb' )
        for chunk in file.chunks( ):
            newfile.write( chunk )

        newfile.close( )

    def abspath(self, name):
        return self.path.join( self.home, name )

    def delete(self, name):
        if self.exists( name ):
            os.remove( self.abspath( name ) )

    def exists(self, name):
        return os.path.exists( self.abspath( name ) )

    def isfile(self, name):
        return os.path.isfile( self.abspath( name ) )

    def isdir(self, name):
        return os.path.isdir( self.abspath( name ) )

    def listdir(self, path, hidden=False):
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

    def accessed_time(self, name):
        return datetime.fromtimestamp( os.path.getatime( self.abspath( name ) ) )

    def created_time(self, name):
        return datetime.fromtimestamp( os.path.getctime( self.abspath( name ) ) )

    def modified_time(self, name):
        return datetime.fromtimestamp( os.path.getmtime( self.abspath( name ) ) )