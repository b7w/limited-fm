# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import File

from django.core.management import call_command
from django.template import Token, TOKEN_BLOCK
from django.template.defaultfilters import filesizeformat
from django.test import TestCase
from django.utils.html import escape
from limited.controls import truncate_path

from limited.models import FileLib, Permission, History, Link
from limited.storage import FileStorage, StoragePath, FileError, FileNotExist
from limited.templatetags.limited_filters import truncatepath, joinpath
from limited.utils import split_path, urlbilder

##
## Main code tests
##
class CodeTest( TestCase ):

    fixtures = ['dump.json']
    
    def test_load_permissions(self):
        print
        print '# Management output start'
        call_command( 'loadpermissions', interactive=False )
        print '# Management end'
        print
        assert Permission.objects.count( ) == 2 ** len( Permission.fields( ) )

    def test_urlbilder(self):
        assert urlbilder( 'action', 2, "add" ) == "/lib2/action/add/"
        assert urlbilder( 'link', "hxhxhxhxhx", r='2' ) == "/link/hxhxhxhxhx/?r=2"
        assert urlbilder( 'link', "habr", r='/path/' ) == "/link/habr/?r=/path/"
        assert urlbilder( 'action', 2, "add", p='test', n='new dir' ) == "/lib2/action/add/?p=test&n=new%20dir"

    def test_split_path(self):
        assert split_path( '' ) == {}
        assert split_path( '/root' ) == {'root':'/root'}
        assert split_path( '/root/path1' ) == {'root':'/root', 'path1':'/root/path1'}
        assert split_path( '/root/path1/path2' ) == {'root':'/root', 'path1':'/root/path1', 'path2':'/root/path1/path2'}
        # test rigth order
        assert split_path( '/c/b/a' ) == {'c':'/c', 'b':'/c/b', 'a':'/c/b/a'}

    def test_truncate_path(self):
        assert truncate_path( 'mordovia forever, karapusi must die' ) == 'mordovia forever, karapusi must die'
        assert truncate_path( 'mordovia forever, karapusi must die', 18 ) == 'mordovia forever,..'
        assert truncate_path( 'mordovia forever, karapusi must die', 20 ).__len__() == 22
        assert truncate_path( 'mordovia forever, karapusi must die', 20, True ).__len__() == 22
        assert truncate_path( 'very long file name.bigext', 20, True ).__len__() == 22
        assert truncate_path( 'very long file name.txt', 10, True) == 'very long..txt'
        
    def test_filter_truncate_path(self):
        assert truncatepath( 'test case '*8 ).__len__() == 64+2
        assert truncatepath( 'test case '*8 , '32' ).__len__() == 32+2
        
        assert truncatepath( 'test case '*8 + '.ext' , 'ext' ).endswith('..ext') == True
        assert truncatepath( 'test case '*8 + '.ext' , 'ext' ).__len__() == 64+2+3
        assert truncatepath( 'test case '*8 + '.ext' , 'noext' ).endswith('..') == True
        assert truncatepath( 'test case '*8 + '.ext' , 'noext' ).__len__() == 64+2
        
        assert truncatepath( 'test case '*8 + '.ext' , '32.ext' ).endswith('..ext') == True
        assert truncatepath( 'test case '*8 + '.ext' , '32.ext' ).__len__() == 32+2+3
        assert truncatepath( 'test case '*8 + '.ext' , '32.noext' ).endswith('..') == True
        assert truncatepath( 'test case '*8 + '.ext' , '32.noext' ).__len__() == 32+2

    def test_tag_joinpath(self):
        token = Token( TOKEN_BLOCK, "{% 'path' 'path2'" )
        node = joinpath( None, token )
        assert [ item.resolve( {} ) for item in node.args ] == [ 'path', 'path2' ]
        assert node.asvar == None

        token = Token( TOKEN_BLOCK, "{% 'path' 'path2' as var" )
        node = joinpath( None, token )
        context = { 'var' : 'xxx', }
        assert [ item.resolve( context ) for item in node.args ] == [ 'path', 'path2' ]
        assert node.asvar == 'var'

        node = joinpath( None, Token( TOKEN_BLOCK, "{% 'path' 'path2' 'file'" ) )
        assert node.render( {} ) == 'path/path2/file'

        node = joinpath( None, Token( TOKEN_BLOCK, "{% '/path' 'path2' 'file'" ) )
        assert node.render( {} ) == 'path/path2/file'

        node = joinpath( None, Token( TOKEN_BLOCK, "{% 'path' 'path2/path3' 'file'" ) )
        assert node.render( {} ) == 'path/path2/path3/file'

        context = { }
        node = joinpath( None, Token( TOKEN_BLOCK, "{% 'path' 'path2' 'file' as path" ) )
        assert node.render( context ) == ''
        assert context['path'] == 'path/path2/file'

        context = { 'var' : 'xxx', }
        node = joinpath( None, Token( TOKEN_BLOCK, "{% '/path' var 'file'" ) )
        assert node.render( context ) == 'path/xxx/file'
        
        context = { 'var' : 'xxx', }
        node = joinpath( None, Token( TOKEN_BLOCK, "{% '/path' var 'file' as path" ) )
        assert node.render( context ) == ''
        assert context['path'] == 'path/xxx/file'

    def test_Model_Permission(self):
        assert Permission.fields().__len__() == 6, "It seems you add permission, correct tests right now"
        assert Permission.fields() == ['edit', 'move', 'delete', 'create', 'upload', 'http_get']
        assert Permission.Full( ) == Permission( edit=True, move=True, delete=True, create=True, upload=True, http_get=True )

    def test_Model_FileLib(self):
        for valid in FileLib.validators:
            self.assertRaises( ValidationError, valid, '/home' )
        for valid in FileLib.validators:
            self.assertRaises( ValidationError, valid, './home' )

        lib = FileLib.objects.get( id=2 )
        assert lib.get_path( '/root/' ) == '/root/test'
        assert lib.get_path( '/root' ) == '/root/test'

    def test_Model_Home(self):
        pass
    
    def test_Model_History(self):
        history = History.objects.get( id=1 )
        assert history.get_type_display() == 'upload'
        assert history.get_image_type() == 'create'
        assert history.is_extra() == False
        assert history.get_extra() == None
        
        history = History.objects.get( id=2 )
        assert history.get_type_display() == 'rename'
        assert history.get_image_type() == 'rename'
        assert history.is_extra() == False
        assert history.get_extra() == None
        
        history = History.objects.get( id=3 )
        assert history.get_type_display() == 'link'
        assert history.get_image_type() == 'create'
        assert history.is_extra() == True
        assert history.get_extra() == '<a href=\"/link/a142a8d1442b/\">direct link</a>'

    def test_Model_Link(self):
        link = Link.objects.get( id=1 )
        assert link.expires() == datetime(2011, 6, 27, 15, 25, 24)



##
## FileStorage tests
##
class FileStorageTest( TestCase ):
    """
    Test are mixed because when we test
    we need to create and delete files after work

    Also much better to run with --failfast

    Best way is to test ``create``, ``mkdir`` and ``clear``
    by your own separately

    To change test data, add them to ``tearDown``
    """

    fixtures = ['dump.json']

    def setUp(self):
        self.path = StoragePath()
        self.lib = FileLib.objects.get( name="Test" )
        self.storage = FileStorage( self.lib.get_path() )

    def tearDown(self):
        # TODO: take out this function
        """
        After run test rollback changes
        For it ``create``, ``mkdir`` and ``clear`` need to work correctly!!
        """
        self.storage.clear( u"" )
        self.storage.mkdir( u".TrashBin" )
        self.storage.mkdir( u".TrashBin/Crash Test" )
        self.storage.mkdir( u"Test Folder" )
        self.storage.create( u"content.txt", u"Test line in file" )
        self.storage.create( u"Фото 007.bin", "007"*2**8 )

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
        abs = self.path.join( settings.LIMITED_ROOT_PATH, self.lib.get_path( ) )
        assert self.storage.abspath( u"file.ext" ) == self.path.join( abs, u"file.ext" )

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
        fileobj.close()
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
        assert self.storage.size( u"content.txt" ) == 17
        assert self.storage.size( u"Test Folder" ) == 0
        assert self.storage.size( u"Test Folder", dir=True ) == 0
        self.storage.create( u"Test Folder/test.bin", "XXX"*2**16 )
        self.storage.create( u"Test Folder/test2.bin", "XXX"*2**16 )
        assert self.storage.size( u"Test Folder", dir=True ) == 196608 + 196608

    def test_list_dir(self):
        """
        Test listdir
        """
        self.assertRaises( FileNotExist, self.storage.listdir, u"No Directory" )
        
        testfolder =  { "class": "dir", "name": u"Test Folder", u"url": "Test%20Folder", "size": 0 }
        testfile =  { "class": "file", 'name': u"content.txt", 'url': "content.txt" }
        testimage = { "class": 'file', "name": u"Фото 007.bin", "url": u"%D0%A4%D0%BE%D1%82%D0%BE%20007.bin" }

        assert self.storage.listdir( "Test Folder" ).__len__() == 0
        assert self.storage.listdir( "", hidden=True ).__len__() == 4

        assert self.storage.listdir( "" ).__len__() == 3
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
        assert self.storage.listfiles( u"Test Folder" ).__len__()  == 0
        
        abs = self.path.join( settings.LIMITED_ROOT_PATH, self.lib.get_path( ) )
        real = {
            self.path.join( abs, u'content.txt' ) : u'content.txt',
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

    def test_other(self):
        """
        Test url, time. Just work it or not
        """
        assert self.storage.url( u"content.txt" ) != None
        assert self.storage.accessed_time( u"content.txt" ) != None
        assert self.storage.created_time( u"content.txt" ) != None
        assert self.storage.modified_time( u"content.txt" ) != None


##
## Action tests
##
class ActionTest( TestCase ):
    """
    Test Action api that need pre and post features
    """

    fixtures = ['dump.json']

    def setUp(self):
        self.path = StoragePath()
        self.lib = FileLib.objects.get( name="Test" )
        self.storage = FileStorage( self.lib.get_path() )

    def tearDown(self):
        # TODO: take out this function
        """
        After run test rollback changes
        For it ``create``, ``mkdir`` and ``clear`` need to work correctly!!
        """
        self.storage.clear( u"" )
        self.storage.mkdir( u".TrashBin" )
        self.storage.mkdir( u".TrashBin/Crash Test" )
        self.storage.mkdir( u"Test Folder" )
        self.storage.create( u"content.txt", u"Test line in file" )
        self.storage.create( u"Фото 007.bin", "007"*2**8 )

    def test_Upload(self):
        """
        Test Upload files
        """
        file1 = self.storage.open( u"content.txt" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [ file1 ] } )
        file1.close()
        assert self.storage.exists( u"Test Folder/content.txt" ) == False

        self.client.login( username='B7W', password='root' )
        file1 = self.storage.open( u"content.txt" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [ file1 ] } )
        file1.close()
        assert self.storage.exists( u"Test Folder/content.txt" ) == True

        file1 = self.storage.open( u"content.txt" )
        file2 = self.storage.open( u"Фото 007.bin" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [ file1, file2, file1 ] } )
        file1.close()
        file2.close()
        assert self.storage.exists( u"Test Folder/content[1].txt" ) == True
        assert self.storage.exists( u"Test Folder/Фото 007.bin" ) == True
        assert self.storage.exists( u"Test Folder/content[2].txt" ) == True



##
## Views tests
##
class ViewsTest( TestCase ):
    
    fixtures = ['dump.json']

    def test_Admin_Homes(self):
        """
        Look home page of admin
        and his libs
        """
        self.assertTrue( self.client.login( username='admin', password='root' ) )
        resp = self.client.get( '/' )
        assert resp.status_code == 200
        assert resp.context['Homes'].__len__( ) == 2
        assert resp.context['Homes'][0].lib.name == 'FileManager'
        assert resp.context['Homes'][1].lib.name == 'Test'

    def test_Anon_Homes(self):
        """
        Look home page of Anonymous
        and his libs
        """
        resp = self.client.get( '/' )
        assert resp.status_code == 200
        assert resp.context['Homes'].__len__( ) == 2
        assert resp.context['Homes'][0].lib.name == 'FileManager'
        assert resp.context['Homes'][1].lib.name == 'Test'

    def test_User_Homes(self):
        """
        Look home page of User
        and his libs
        """
        assert self.client.login( username='B7W', password='root' )
        resp = self.client.get( '/' )
        assert resp.status_code == 200
        assert resp.context['Homes'].__len__( ) == 1
        assert resp.context['Homes'][0].lib.name == 'Test'
        assert resp.context['AnonHomes'].__len__( ) == 1
        assert resp.context['AnonHomes'][0].lib.name == 'FileManager'

    def test_Admin_Trash(self):
        """
        Test Trash of file libs for Admin
        """
        lib = FileLib.objects.get( name='FileManager' )
        storage = FileStorage( lib.get_path() )
        if storage.exists( u".TrashBin" ):
            storage.remove( u".TrashBin" )
        resp = self.client.get( urlbilder( 'trash', lib.id ) )
        assert storage.exists( u".TrashBin" )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 0

        lib = FileLib.objects.get( name='Test' )
        resp = self.client.get( urlbilder( 'trash', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 1

        resp = self.client.get( urlbilder( 'trash', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode(resp.content, errors='ignore')

    def test_Anon_Trash(self):
        """
        Test Trash of file libs for Anonymous
        """
        self.assertTrue( self.client.login( username='admin', password='root' ) )
        lib = FileLib.objects.get( name='FileManager' )
        resp = self.client.get( urlbilder( 'trash', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 0

        lib = FileLib.objects.get( name='Test' )
        resp = self.client.get( urlbilder( 'trash', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 1

        resp = self.client.get( urlbilder( 'trash', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode(resp.content, errors='ignore')

    def test_User_Trash(self):
        """
        Test Trash of file libs for User
        """
        assert self.client.login( username='B7W', password='root' )
        lib = FileLib.objects.get( name='FileManager' )
        resp = self.client.get( urlbilder( 'trash', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 0

        lib = FileLib.objects.get( name='Test' )
        resp = self.client.get( urlbilder( 'trash', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 1

        resp = self.client.get( urlbilder( 'trash', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode(resp.content, errors='ignore')

    def test_Admin_History(self):
        """
        Test History of History for Admin
        """
        lib = FileLib.objects.get( name='FileManager' )
        resp = self.client.get( urlbilder( 'history', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 0

        lib = FileLib.objects.get( name='Test' )
        resp = self.client.get( urlbilder( 'history', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 3

        resp = self.client.get( urlbilder( 'history', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode(resp.content, errors='ignore')

    def test_Anon_History(self):
        """
        Test History of History for Anonymous
        """
        self.assertTrue( self.client.login( username='admin', password='root' ) )
        lib = FileLib.objects.get( name='FileManager' )
        resp = self.client.get( urlbilder( 'history', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 0

        lib = FileLib.objects.get( name='Test' )
        resp = self.client.get( urlbilder( 'history', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 3

        resp = self.client.get( urlbilder( 'history', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode(resp.content, errors='ignore')

    def test_User_History(self):
        """
        Test History of History for User
        """
        assert self.client.login( username='B7W', password='root' )
        lib = FileLib.objects.get( name='FileManager' )
        resp = self.client.get( urlbilder( 'history', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 0

        lib = FileLib.objects.get( name='Test' )
        resp = self.client.get( urlbilder( 'history', lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 3

        resp = self.client.get( urlbilder( 'history', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode(resp.content, errors='ignore')

    def test_Login(self):
        """
        Test login page and redirect to login page
        """
        resp = self.client.get( urlbilder( 'login' ) )
        assert resp.status_code == 200

    def test_Dosnt_Exists(self):
        """
        Test Error doesn't exist of file or FileLib
        """
        lib = FileLib.objects.get( name='Test' )
        resp = self.client.get( urlbilder( 'browser', lib.id, p="None" ) )
        assert resp.status_code == 200
        assert escape( u"path 'None' doesn't exist or it isn't a directory" ) in unicode(resp.content, errors='ignore')

        resp = self.client.get( urlbilder( 'browser', 10, p="None" ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode(resp.content, errors='ignore')
        
    def test_Index_History_Widget(self):
        """
        Test that for Anonymous, Users, Admin
        we see equal history
        with actions from all users!
        """
        resp = self.client.get( '/' )
        assert resp.status_code == 200
        assert 1 in [x.id for x in resp.context['history']]
        assert 2 in [x.id for x in resp.context['history']]
        assert 3 in [x.id for x in resp.context['history']]

        self.client.login( username='admin', password='root' )
        resp = self.client.get( '/' )
        assert resp.status_code == 200
        assert 1 in [x.id for x in resp.context['history']]
        assert 2 in [x.id for x in resp.context['history']]
        assert 3 in [x.id for x in resp.context['history']]
        self.client.logout( )

        self.client.login( username='B7W', password='root' )
        resp = self.client.get( '/' )
        assert resp.status_code == 200
        assert 1 in [x.id for x in resp.context['history']]
        assert 2 in [x.id for x in resp.context['history']]
        assert 3 in [x.id for x in resp.context['history']]
        self.client.logout( )

    def test_Anon_Action(self):
        """
        Test Action for Anonymous
        in  ID1: FileManager
        with  ID5: Edit False, Move False, Delete False, Create True, Upload False, Http_get False,
        """
        lib = FileLib.objects.get( name='FileManager' )
        storage = FileStorage( lib.get_path() )
        # add True
        link = urlbilder( 'action', lib.id, "add", p='', n='new dir' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'created' in [m.message for m in list( resp.context['messages'] )][0]
        storage.remove( storage.path.join( '', 'new dir' ) )
        # delete False
        link = urlbilder( 'action', lib.id, "delete", p=u"Фото 007.bin" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # trash False
        link = urlbilder( 'action', lib.id, "trash", p=u"Фото 007.bin"  )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # rename False
        link = urlbilder( 'action', lib.id, "rename", p=u"Фото 007.bin" , n='Фото070.jpg' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # move False
        link = urlbilder( 'action', lib.id, "move", p=u"Фото 007.bin" , n='/' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # link True
        link = urlbilder( 'action', lib.id, "link", p=u"Фото 007.bin"  )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'link' in [m.message for m in list( resp.context['messages'] )][0]
        # zip False
        link = urlbilder( 'action', lib.id, "zip", p=u"Фото 007.bin" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # size very simple dir test
        link = urlbilder( 'action', lib.id, "size", p='debug_toolbar' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        size = filesizeformat( storage.size( 'debug_toolbar', dir=True, cached=False ) )
        assert size == resp.content.strip()

    def test_Path_Arr(self):
        """
        Test ``class="breadcrumbs"`` in html or ``patharr`` in template interpretation.

        The order is not important because we already check it in ``CodeTest.test_split_path``
        """
        lib = FileLib.objects.get( name='FileManager' )
        link = urlbilder( 'browser', lib.id, p='limited/templatetags' )
        resp = self.client.get( link )
        assert '<a href="/">#Home</a>' in resp.content
        assert '<a href="/lib1/">FileManager</a>' in resp.content
        assert '<a href="/lib1/?p=limited">limited</a>' in resp.content
        assert 'templatetags' in resp.content

    def test_Download(self):
        """
        Test response of download page
        """
        lib = FileLib.objects.get( name='Test' )

        link = urlbilder( u'download', lib.id, p=u'content.txt' )
        resp = self.client.get( link )
        assert resp.status_code == 200

        link = urlbilder( u'download', lib.id, p=u'Test Folder' )
        resp = self.client.get( link )
        assert resp.status_code == 200

        link = urlbilder( u'link', u"nosuchhash" )
        resp = self.client.get( link )
        assert resp.status_code == 200
        assert escape( u"We are sorry. But such object does not exists or link is out of time" ) in unicode(resp.content, errors='ignore')
        
        hash =  Link.objects.get( id=1 ).hash
        link = urlbilder( 'link', hash )
        resp = self.client.get( link )
        assert resp.status_code == 200
        assert escape( u"No file or directory find" ) not in unicode(resp.content, errors='ignore')
