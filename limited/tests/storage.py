# -*- coding: utf-8 -*-

import time

from django.conf import settings
from django.core.files.base import File

from limited.controls import clear_folders
from limited.storage.base import FileError, FileNotExist
from limited.storage.utils import ZipThread
from limited.tests.base import StorageTestCase


class FileStorageTest( StorageTestCase ):
    """
    Test are mixed because when we test
    we need to create and delete files after work
    """

    def test_storage_path(self):
        """
        Test StoragePath class
        """
        assert self.path.join( u"path", "name" ) == u"path/name"
        assert self.path.join( u"/path", "name" ) == u"/path/name"
        assert self.path.join( u"/root/path", "name" ) == u"/root/path/name"
        assert self.path.join( u"/path/", "name" ) == u"/path/name"
        assert self.path.join( u"/path/", "/name" ) != u"/path/name", " = /name"

        assert self.path.name( u"/path/name" ) == u"name"
        assert self.path.name( u"/path/name" ) == u"name"
        assert self.path.name( u"/path/name/" ) == u""

        assert self.path.dirname( u"/path/name/" ) == u"/path/name"
        assert self.path.dirname( u"/path/name/file" ) == u"/path/name"
        assert self.path.dirname( u"/path/name/file.ext" ) == u"/path/name"

        assert self.path.norm( u"/root/base", "file.ext" ) == u"file.ext"
        assert self.path.norm( u"/root/base", "../file.ext" ) == u"root/file.ext"
        assert self.path.norm( u"/root/base", ".././file.ext" ) == u"root/file.ext"
        assert self.path.norm( u"/root/base", "../../file.ext" ) == u"file.ext"
        assert self.path.norm( u"/root", "./file.ext" ) == u"root/file.ext"
        assert self.path.norm( u"/root", "././file.ext" ) == u"root/file.ext"

    def test_storage_open(self):
        """
        Try to read content from file
        """
        f = self.storage.open( u"content.txt" )
        content = f.read( )
        f.close( )
        assert content.strip( ) == u"Test line in file"

    def test_abspath(self):
        """
        Simple check for ``get Absolute``
        """
        assert self.storage.abspath( u"file.ext" ) == self.lib.get_path( ) + u'/' + u"file.ext"

    def test_homepath(self):
        """
        Simple check for ``get Absolute``
        """
        assert self.storage.homepath( u"file.ext" ) == self.lib.path + u'/' + u"file.ext"

    def test_is(self):
        """
        Test ``exists``, ``is file``, ``is dir`` on already created 'Test Folder'
        """
        assert self.storage.exists( u"Test Folder" ) == True
        assert self.storage.isdir( u"Test Folder" ) == True
        assert self.storage.isfile( u"Test Folder" ) == False

    def test_create(self):
        """
        Try to create file with content and read it back
        """
        self.storage.create( u"Test Folder/test.bin", u"Test" )
        assert self.storage.exists( u"Test Folder/test.bin" ) == True
        assert self.storage.isfile( u"Test Folder/test.bin" ) == True
        f = self.storage.open( u"Test Folder/test.bin" )
        content = f.read( )
        f.close( )
        assert content.strip( ) == u"Test"

    def test_save(self):
        """
        Test save file obj to disk
        """
        fileobj = self.storage.open( u"content.txt" )
        self.storage.save( u"test file.bin", File( fileobj ) )
        fileobj.close( )
        assert self.storage.exists( u"test file.bin" ) == True
        f = self.storage.open( u"test file.bin" )
        content = f.read( )
        f.close( )
        assert content.strip( ) == u"Test line in file"
        self.storage.remove( u"test file.bin" )

    def test_remove(self):
        """
        Test removing of files and directories, recursive
        """
        self.assertRaises( FileNotExist, self.storage.remove, u"No Folder" )

        self.storage.mkdir( u"New dir" )
        self.storage.remove( u"New dir" )
        assert self.storage.exists( u"New dir" ) == False

        self.storage.create( u"test.bin", u"Test" )
        self.storage.remove( u"test.bin" )
        assert self.storage.exists( u"test.bin" ) == False

    def test_clear(self):
        """
        Test clear and test and very similar 'controls.clear_folders'
        """
        self.assertRaises( FileNotExist, self.storage.clear, u"No Folder" )
        self.assertRaises( FileError, self.storage.clear, u"content.txt" )

        self.storage.clear( u".TrashBin", older=60 )
        assert self.storage.exists( u".TrashBin/Crash Test" ) == True
        time.sleep( 1 )
        self.storage.clear( u".TrashBin", older=1 )
        assert self.storage.exists( u".TrashBin/Crash Test" ) == False

        self.storage.create( u".TrashBin/test.bin", u"Test" )
        clear_folders( u"NoFolder" )
        clear_folders( u".TrashBin", 0 )
        assert self.storage.exists( u".TrashBin/test.bin" ) == False

    def test_mkdir(self):
        """
        Test directory creating
        """
        self.assertRaises( FileError, self.storage.mkdir, u"Test Folder" )
        self.storage.mkdir( u"New dir" )
        assert self.storage.exists( u"New dir" ) == True
        assert self.storage.isdir( u"New dir" ) == True
        assert self.storage.isfile( u"New dir" ) == False

    def test_move(self):
        """
        Test moving of files and directories, recursive
        """
        self.assertRaises( FileError, self.storage.move, u"Test Folder", u"Test Folder" )
        self.assertRaises( FileNotExist, self.storage.move, u"No Folder", u"Some Folder" )
        self.assertRaises( FileNotExist, self.storage.move, u"Test Folder", u"No Folder" )
        self.storage.mkdir( u"New dir" )
        self.storage.create( u"New dir/test.bin", u"Test" )
        self.storage.create( u"New dir/test2.bin", u"Test" )

        self.storage.move( u"New dir/test.bin", u"Test Folder" )
        assert self.storage.exists( u"New dir/test.bin" ) == False
        assert self.storage.exists( u"Test Folder/test.bin" ) == True

        self.storage.move( u"New dir", u"Test Folder" )
        assert self.storage.exists( u"New dir" ) == False
        assert self.storage.exists( u"Test Folder/New dir" ) == True
        assert self.storage.exists( u"Test Folder/New dir/test2.bin" ) == True

    def test_rename(self):
        """
        Test rename of files and directories
        """
        self.assertRaises( FileError, self.storage.rename, u"content.txt", u"bad/file.ext" )
        self.assertRaises( FileNotExist, self.storage.rename, u"no file.txt", u"Фото 007.bin" )
        self.assertRaises( FileError, self.storage.rename, u"content.txt", u"Фото 007.bin" )
        self.storage.mkdir( u"New dir" )
        self.storage.create( u"New dir/test.bin", u"Test" )

        self.storage.rename( u"New dir/test.bin", u"test2.bin" )
        assert self.storage.exists( u"New dir/test2.bin" ) == True

        self.storage.rename( u"New dir", u"New dir 2" )
        assert self.storage.exists( u"New dir 2" ) == True
        assert self.storage.exists( u"New dir 2/test2.bin" ) == True

    def test_trash(self):
        """
        Test moving to trash files and directories
        """
        self.assertRaises( FileNotExist, self.storage.totrash, u"no file" )
        self.storage.mkdir( u"Crash Test" )
        self.storage.create( u"Crash Test/test.bin", u"Test" )

        self.storage.remove( u".TrashBin" )
        self.storage.totrash( u"Crash Test/test.bin" )
        assert self.storage.exists( u".TrashBin" ) == True
        assert self.storage.exists( u".TrashBin/test.bin" ) == True

        self.storage.totrash( u"Crash Test" )
        assert self.storage.exists( u".TrashBin/Crash Test" ) == True

    def test_size(self):
        """
        Test size
        """
        assert self.storage.size( u"content.txt", cached=False ) == 17
        assert self.storage.size( u"Test Folder", cached=False ) == 0
        assert self.storage.size( u"Test Folder", dir=True, cached=False ) == 0
        self.storage.create( u"Test Folder/test.bin", "XXX" * 2 ** 16 )
        self.storage.create( u"Test Folder/test2.bin", "XXX" * 2 ** 16 )
        assert self.storage.size( u"Test Folder", dir=True, cached=False ) == 196608 + 196608

    def test_list_dir(self):
        """
        Test listdir
        """
        self.assertRaises( FileNotExist, self.storage.listdir, u"No Directory" )

        testfolder = { "class": "dir", "name": u"Test Folder", u"url": "Test%20Folder", "size": 0 }
        testfile = { "class": "file", 'name': u"content.txt", 'url': "content.txt" }
        testimage = { "class": 'file', "name": u"Фото 007.bin", "url": u"%D0%A4%D0%BE%D1%82%D0%BE%20007.bin" }

        assert self.storage.listdir( "Test Folder" ).__len__( ) == 0
        assert self.storage.listdir( "", hidden=True ).__len__( ) == 4

        assert self.storage.listdir( "" ).__len__( ) == 3
        assert self.storage.listdir( "" )[0]['class'] == testfolder['class']
        assert self.storage.listdir( "" )[0]['name'] == testfolder['name']
        assert self.storage.listdir( "" )[0]['url'] == testfolder['url']
        assert self.storage.listdir( "" )[0]['size'] == testfolder['size']

        assert self.storage.listdir( "" )[1]['class'] == testfile['class']
        assert self.storage.listdir( "" )[1]['name'] == testfile['name']
        assert self.storage.listdir( "" )[1]['url'] == testfile['url']

        assert self.storage.listdir( "" )[2]['class'] == testimage['class']
        assert self.storage.listdir( "" )[2]['name'] == testimage['name']
        assert self.storage.listdir( "" )[2]['url'] == testimage['url']

    def test_list_files(self):
        """
        Test listfiles
        """
        assert self.storage.listfiles( u"Test Folder" ).__len__( ) == 0

        abs = self.path.join( settings.LIMITED_ROOT_PATH, self.lib.get_path( ) )
        real = {
            self.path.join( abs, u'content.txt' ): u'content.txt',
            self.path.join( abs, u"Фото 007.bin" ): u"Фото 007.bin",
            }
        assert self.storage.listfiles( "" ) == real

        self.storage.create( u"Test Folder/test.bin", u"Test" )
        real.update( { self.path.join( abs, u'Test Folder/test.bin' ): u'Test Folder/test.bin' } )
        assert self.storage.listfiles( "" ) == real

    def test_available_name(self):
        """
        Test reservation of file name
        """
        assert self.storage.available_name( u"file name.ext" ) == u"file name.ext"
        self.storage.create( u"file name.ext", u"Test" )
        assert self.storage.available_name( u"file name.ext" ) == u"file name[1].ext"
        self.storage.create( u"file name[1].ext", u"Test" )
        assert self.storage.available_name( u"file name.ext" ) == u"file name[2].ext"

    def test_zip(self):
        """
        Test zip, unzip for files and folders
        """
        self.storage.zip( u"content.txt" )
        assert self.storage.exists( u"content.txt.zip" ) == True
        self.storage.move( u"content.txt.zip", u"Test Folder" )

        self.storage.unzip( u"Test Folder/content.txt.zip" )
        assert self.storage.exists( u"Test Folder/content.txt" ) == True

        self.storage.zip( u"Test Folder" )
        assert self.storage.exists( u"Test Folder.zip" ) == True
        self.storage.move( u"Test Folder.zip", u"Test Folder" )
        self.storage.unzip( u"Test Folder/Test Folder.zip" )
        assert self.storage.exists( u"Test Folder/Test Folder/content.txt" ) == True

    def test_download(self):
        """
        Test download in Thread
        """
        self.storage.download( u"logo3w.png", u"http://www.google.ru/images/srpr/logo3w.png" )
        time.sleep( 2 )
        assert self.storage.exists( u"logo3w.png" ) == True

    def test_zip_thread(self):
        """
        Test zip in Thread
        """
        th = ZipThread( self.storage, u"Test Folder", u"Test Folder.zip" )
        th.start( )
        th.join( )
        assert self.storage.exists( u"Test Folder.zip" ) == True

    def test_other(self):
        """
        Test url, time. Just work it or not
        """
        assert self.storage.url( u"content.txt" ) != None
        assert self.storage.accessed_time( u"content.txt" ) != None
        assert self.storage.created_time( u"content.txt" ) != None
        assert self.storage.modified_time( u"content.txt" ) != None