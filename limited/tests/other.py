# -*- coding: utf-8 -*-

from limited import settings
from django.core.exceptions import ValidationError

from django.core.management import call_command
from django.template import Token, TOKEN_BLOCK
from django.test import TestCase

from limited.controls import truncate_path
from limited.models import FileLib, Permission, History
from limited.templatetags.limited_filters import truncatepath, joinpath
from limited.utils import split_path, urlbilder, url_get_filename


class CodeTest( TestCase ):
    fixtures = ['dump.json']

    def test_load_permissions(self):
        """
        Test management command loadpermissions.
        """
        print
        print '# Management output start'
        call_command( 'loadpermissions', interactive=False )
        print '# Management end'
        print
        assert Permission.objects.count( ) == 2 ** len( Permission.fields( ) )

    def test_clear_folder(self):
        """
        Test management command clearfolder.
        If no exceptions - pretty good
        """
        call_command( 'clearfolder', settings.LIMITED_TRASH_PATH )
        call_command( 'clearfolder', settings.LIMITED_TRASH_PATH, '24*60*60' )
        call_command( 'clearfolder', 'NoFolder', '24*60*60' )

    def test_urlbilder(self):
        assert urlbilder( 'action', 2, "add" ) == "/lib2/action/add/"
        assert urlbilder( 'link', "hxhxhxhxhx", r='2' ) == "/link/hxhxhxhxhx/?r=2"
        assert urlbilder( 'link', "habr", r='/path/' ) == "/link/habr/?r=/path/"
        assert urlbilder( 'action', 2, "add", p='test', n='new dir' ) == "/lib2/action/add/?p=test&n=new%20dir"

    def test_url_get_filename(self):
        assert url_get_filename( u"http://www.djangoproject.com/download/1.3/tarball/" ) == u"tarball"
        assert url_get_filename( u"http://domen.ru/share/2033.fb2" ) == u"2033.fb2"
        assert url_get_filename( u"http://domen.ru/share/Исчисление высказываний.pdf" ) == u"Исчисление высказываний.pdf"

    def test_split_path(self):
        assert split_path( '' ) == []
        assert split_path( '/root' ) == [('root', '/root')]
        assert split_path( '/root/path1' ) == [('root', '/root'), ('path1', '/root/path1')]
        assert split_path( '/root/path1/path2' ) == [('root', '/root'), ('path1', '/root/path1'),
            ('path2', '/root/path1/path2')]
        assert split_path( '/root/path/path' ) == [('root', '/root'), ('path', '/root/path'),
            ('path', '/root/path/path')]
        # test rigth order
        assert split_path( '/c/b/a' ) == [('c', '/c'), ('b', '/c/b'), ('a', '/c/b/a')]

    def test_truncate_path(self):
        assert truncate_path( 'mordovia forever, karapusi must die' ) == 'mordovia forever, karapusi must die'
        assert truncate_path( 'mordovia forever, karapusi must die', 18 ) == 'mordovia forever,..'
        assert truncate_path( 'mordovia forever, karapusi must die', 20 ).__len__( ) == 22
        assert truncate_path( 'mordovia forever, karapusi must die', 20, True ).__len__( ) == 22
        assert truncate_path( 'very long file name.bigext', 20, True ).__len__( ) == 22
        assert truncate_path( 'very long file name.txt', 10, True ) == 'very long..txt'

    def test_filter_truncate_path(self):
        assert truncatepath( 'test case ' * 8 ).__len__( ) == 64 + 2
        assert truncatepath( 'test case ' * 8, '32' ).__len__( ) == 32 + 2

        assert truncatepath( 'test case ' * 8 + '.ext', 'ext' ).endswith( '..ext' ) == True
        assert truncatepath( 'test case ' * 8 + '.ext', 'ext' ).__len__( ) == 64 + 2 + 3
        assert truncatepath( 'test case ' * 8 + '.ext', 'noext' ).endswith( '..' ) == True
        assert truncatepath( 'test case ' * 8 + '.ext', 'noext' ).__len__( ) == 64 + 2

        assert truncatepath( 'test case ' * 8 + '.ext', '32.ext' ).endswith( '..ext' ) == True
        assert truncatepath( 'test case ' * 8 + '.ext', '32.ext' ).__len__( ) == 32 + 2 + 3
        assert truncatepath( 'test case ' * 8 + '.ext', '32.noext' ).endswith( '..' ) == True
        assert truncatepath( 'test case ' * 8 + '.ext', '32.noext' ).__len__( ) == 32 + 2

    def test_tag_joinpath(self):
        token = Token( TOKEN_BLOCK, "{% 'path' 'path2'" )
        node = joinpath( None, token )
        assert [item.resolve( { } ) for item in node.args] == ['path', 'path2']
        assert node.asvar == None

        token = Token( TOKEN_BLOCK, "{% 'path' 'path2' as var" )
        node = joinpath( None, token )
        context = { 'var': 'xxx', }
        assert [item.resolve( context ) for item in node.args] == ['path', 'path2']
        assert node.asvar == 'var'

        node = joinpath( None, Token( TOKEN_BLOCK, "{% 'path' 'path2' 'file'" ) )
        assert node.render( { } ) == 'path/path2/file'

        node = joinpath( None, Token( TOKEN_BLOCK, "{% '/path' 'path2' 'file'" ) )
        assert node.render( { } ) == 'path/path2/file'

        node = joinpath( None, Token( TOKEN_BLOCK, "{% 'path' 'path2/path3' 'file'" ) )
        assert node.render( { } ) == 'path/path2/path3/file'

        context = { }
        node = joinpath( None, Token( TOKEN_BLOCK, "{% 'path' 'path2' 'file' as path" ) )
        assert node.render( context ) == ''
        assert context['path'] == 'path/path2/file'

        context = { 'var': 'xxx', }
        node = joinpath( None, Token( TOKEN_BLOCK, "{% '/path' var 'file'" ) )
        assert node.render( context ) == 'path/xxx/file'

        context = { 'var': 'xxx', }
        node = joinpath( None, Token( TOKEN_BLOCK, "{% '/path' var 'file' as path" ) )
        assert node.render( context ) == ''
        assert context['path'] == 'path/xxx/file'

    def test_Model_Permission(self):
        assert Permission.fields( ).__len__( ) == 6, "It seems you add permission, correct tests right now"
        assert Permission.fields( ) == ['edit', 'move', 'delete', 'create', 'upload', 'http_get']
        assert Permission.Full( ) == Permission( edit=True, move=True, delete=True, create=True, upload=True,
                                                 http_get=True )

    def test_Model_FileLib(self):
        for valid in FileLib.validators:
            self.assertRaises( ValidationError, valid, '/home' )
        for valid in FileLib.validators:
            self.assertRaises( ValidationError, valid, './home' )

        lib = FileLib.objects.get( id=2 )
        assert lib.get_path( '/root/' ) == '/root/test'
        assert lib.get_path( '/root' ) == '/root/test'

    def test_Model_History(self):
        history = History.objects.get( id=1 )
        assert history.get_type_display( ) == 'upload'
        assert history.get_image_type( ) == 'create'
        assert history.is_extra( ) == False
        assert history.get_extra( ) == None

        history = History.objects.get( id=2 )
        assert history.get_type_display( ) == 'rename'
        assert history.get_image_type( ) == 'rename'
        assert history.is_extra( ) == False
        assert history.get_extra( ) == None

        history = History.objects.get( id=3 )
        assert history.get_type_display( ) == 'link'
        assert history.get_image_type( ) == 'create'
        assert history.is_extra( ) == True
        assert history.get_extra( ) == '<a href=\"/link/d89d9baa47e8/\">direct link</a>'