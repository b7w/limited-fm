# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import errno
import urllib
import zipfile

from django.core.files.base import File
from django.utils.encoding import iri_to_uri

from limited.files.api.base import file_pre_change, FileStorageBaseApi
from limited.files.storage import FileError, FilePath, FileNotExist

class FileStorageExtra( FileStorageBaseApi ):
    """
    File Storage additional class
    """

    def create(self, path, content, signal=True ):
        """
        Write to file ``path`` same data ``content``
        """
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        newfile = self.fs.open( path, 'wb' )
        newfile.write( content )
        newfile.close( )

    def download(self, url, path, signal=True):
        """
        Download file from ``url`` to file ``path``.
        The process goes to a file ``path + '.part'``.
        On error file will be remove.
        To get file name from url use :class:`~limited.utils.url_get_filename`.
        """
        path = self.check( path )
        path = self.fs.available_name( path )
        newfile = path + u".part"
        try:
            # simple hook to stop File proxy access field 'name'
            # that is no exists
            if signal:
                file_pre_change.send( self, basedir=FilePath.dirname( path ) )
            data = urllib.urlopen( iri_to_uri( url ) )
            data.size = int( data.info( )['Content-Length'] )
            self.fs.save( newfile, File( data ) )
            self.fs.rename( newfile, FilePath.name( path ) )
        except Exception:
            if self.fs.exists( newfile ):
                self.fs.remove( newfile )
            raise

    def zip(self, path, file=None, override=None, signal=False):
        """
        Zip file or directory ``path`` to ``file`` or to ``path + '.zip'``.
        On not exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        path = self.check( path )
        if self.fs.exists( path ) == False:
            raise FileNotExist( u"'%s' not found" % path )

        if file == None:
            file = self.available_name( path + u".zip", override=override )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )

        newfile = file + u".part"
        try:
            zfile = self.fs.open( newfile, mode='wb' )
            archive = zipfile.ZipFile( zfile, 'w', zipfile.ZIP_DEFLATED )
            if self.fs.isdir( path ):
                dirname = FilePath.name( path )
                for abspath, name in self.fs.listfiles( path ).items( ):
                    name = FilePath.join( dirname, name )
                    archive.write( abspath, name )
            elif self.fs.isfile( path ):
                archive.write( self.fs.abspath( path ), FilePath.name( path ) )

            archive.close( )
            zfile.seek( 0 )
            self.fs.rename( newfile, FilePath.name( file ) )
        except EnvironmentError as e:
            if e.errno == errno.EACCES:
                raise FileError( u"IOError, zip. Permission denied '%s'" % name )
        finally:
            if self.fs.exists( newfile ):
                self.fs.remove( newfile )

    def unzip(self, path, override=True, signal=False):
        """
        Unzip file or directory ``path``.
        On not exist raise :class:`~limited.files.storage.FileNotExist`.
        """
        path = self.check( path )
        if not self.fs.exists( path ):
            raise FileNotExist( u"'%s' not found" % path )

        file = self.fs.abspath( path )
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


    def clear(self, path, older=None, signal=True ):
        """
        Remove all files and dirs in ``path`` directory.
        ``older`` takes seconds for max age from created_time, only top sub dirs checked.
        On not exist raise :class:`~limited.files.storage.FileNotExist`.
        On not directory raise :class:`~limited.files.storage.FileError`.
        """
        path = self.check( path )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )

        if not self.fs.exists( path ):
            raise FileNotExist( u"'%s' not found" % path )
        if not self.fs.isdir( path ):
            raise FileError( u"'%s' not directory" % path )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        if older == None:
            for item in self.fs.list( path ):
                file = FilePath.join( path, item )
                self.fs.remove( file )
        else:
            for item in self.fs.list( path ):
                file = FilePath.join( path, item )
                chenaged = self.fs.created_time( file )
                if datetime.now( ) - chenaged > timedelta( seconds=older ):
                    self.fs.remove( file )