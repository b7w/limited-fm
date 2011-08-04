# -*- coding: utf-8 -*-

from django.core.management import call_command
from django.test import TestCase
from limited.controls import truncate_path

from limited.models import MFileLib, MPermission
from limited.storage import FileStorage
from limited.utils import split_path,urlbilder


class CodeTest( TestCase ):
    def test_load_permissions(self):
        print
        print '# Management output start'
        call_command( 'loadpermissions', interactive=False )
        print '# Management end'
        print
        assert MPermission.objects.count( ) == 2 ** len( MPermission.fields( ) )

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
        lib = MFileLib.objects.get( name='FileManager' )
        storage = FileStorage( lib.get_path() )
        # add True
        link = urlbilder( 'action', lib.id, "add", p='test', n='new dir' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'created' in [m.message for m in list( resp.context['messages'] )][0]
        storage.delete( storage.path.join( 'test', 'new dir' ) )
        # delete False
        link = urlbilder( 'action', lib.id, "delete", p='test/Фото 070.jpg' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # trash False
        link = urlbilder( 'action', lib.id, "trash", p='test/Фото 070.jpg' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # rename False
        link = urlbilder( 'action', lib.id, "rename", p='test/Фото 070.jpg', n='Фото070.jpg' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # move False
        link = urlbilder( 'action', lib.id, "move", p='test/Фото 070.jpg', n='/' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # link True
        link = urlbilder( 'action', lib.id, "link", p='test/Фото 070.jpg' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'link' in [m.message for m in list( resp.context['messages'] )][0]
        # zip False
        link = urlbilder( 'action', lib.id, "zip", p='test/Фото 070.jpg' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # size very simple dir test
        link = urlbilder( 'action', lib.id, "size", p='debug_toolbar' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert '672.5 KB' in resp.content

    def test_Path_Arr(self):
        """
        Test ``class="breadcrumbs"`` in html or ``patharr`` in template interpretation.

        The order is not important because we already check it in ``CodeTest.test_split_path``
        """
        link = urlbilder( 'browser', 1, p='limited/templatetags' )
        resp = self.client.get( link )
        assert '<a href="/">#Home</a>' in resp.content
        assert '<a href="/lib1/">FileManager</a>' in resp.content
        assert '<a href="/lib1/?p=limited">limited</a>' in resp.content
        assert 'templatetags' in resp.content
