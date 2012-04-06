# -*- coding: utf-8 -*-


from django.template.defaultfilters import filesizeformat
from django.utils.html import escape

from limited.core import settings
from limited.core.models import  Link
from limited.core.files.utils import FilePath
from limited.core.tests.base import StorageTestCase
from limited.core.utils import urlbilder

class ViewsTest( StorageTestCase ):
    def test_Anon_Redirects(self):
        """
        Test redirect to login page when user is Anonymous
        and settings.LIMITED_ANONYMOUS = False
        """

        assert self.client.get( '/' ).status_code == 302
        assert self.client.get( urlbilder( 'browser', 1 ) ).status_code == 302
        assert self.client.get( urlbilder( 'trash', 1 ) ).status_code == 302
        assert self.client.get( urlbilder( 'history', 1 ) ).status_code == 302
        assert self.client.get( urlbilder( 'action', 1, 'delete', p='' ) ).status_code == 302
        assert self.client.get( urlbilder( 'clear', 1, 'cache' ) ).status_code == 302
        assert self.client.get( urlbilder( 'download', 1 ) ).status_code == 302
        assert self.client.get( urlbilder( 'upload', 1 ) ).status_code == 302


    def test_Admin_Homes(self):
        """
        Look home page of admin
        and his libs
        """
        assert self.client.login( username='admin', password='root' )

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
        self.setAnonymous( True )

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
        assert self.client.login( username='admin', password='root' )

        if self.storage2.exists( settings.LIMITED_TRASH_PATH ):
            self.storage2.remove( settings.LIMITED_TRASH_PATH )
        resp = self.client.get( urlbilder( 'trash', self.lib2.id ) )
        assert self.storage2.exists( settings.LIMITED_TRASH_PATH ) == True
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 0

        resp = self.client.get( urlbilder( 'trash', self.lib.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 1

        resp = self.client.get( urlbilder( 'trash', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

    def test_Anon_Trash(self):
        """
        Test Trash of file libs for Anonymous
        """
        self.setAnonymous( True )

        resp = self.client.get( urlbilder( 'trash', self.lib2.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 0

        resp = self.client.get( urlbilder( 'trash', self.lib.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 1

        resp = self.client.get( urlbilder( 'trash', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

    def test_User_Trash(self):
        """
        Test Trash of file libs for User
        """
        self.setAnonymous( True )
        assert self.client.login( username='B7W', password='root' )

        resp = self.client.get( urlbilder( 'trash', self.lib2.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 0

        resp = self.client.get( urlbilder( 'trash', self.lib.id ) )
        assert resp.status_code == 200
        assert resp.context['files'].__len__( ) == 1

        resp = self.client.get( urlbilder( 'trash', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

    def test_Admin_History(self):
        """
        Test History of History for Admin
        """
        assert self.client.login( username='admin', password='root' )

        resp = self.client.get( urlbilder( 'history', self.lib2.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 0

        resp = self.client.get( urlbilder( 'history', self.lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 3

        resp = self.client.get( urlbilder( 'history', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

    def test_Anon_History(self):
        """
        Test History of History for Anonymous
        """
        self.setAnonymous( True )

        resp = self.client.get( urlbilder( 'history', self.lib2.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 0

        resp = self.client.get( urlbilder( 'history', self.lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 3

        resp = self.client.get( urlbilder( 'history', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

    def test_User_History(self):
        """
        Test History of History for User
        """
        self.setAnonymous( True )
        assert self.client.login( username='B7W', password='root' )

        resp = self.client.get( urlbilder( 'history', self.lib2.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 0

        resp = self.client.get( urlbilder( 'history', self.lib.id ) )
        assert resp.status_code == 200
        assert resp.context['history'].__len__( ) == 3

        resp = self.client.get( urlbilder( 'history', 10 ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

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
        assert self.client.login( username='B7W', password='root' )

        resp = self.client.get( urlbilder( 'browser', self.lib.id, p="None" ) )
        assert resp.status_code == 200
        assert escape( u"path 'None' doesn't exist or it isn't a directory" ) in unicode( resp.content, errors='ignore' )

        resp = self.client.get( urlbilder( 'browser', 10, p="None" ) )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

    def test_Index_History_Widget(self):
        """
        Test that for Anonymous, Users, Admin
        we see equal history
        with actions from all users!
        """
        self.setAnonymous( True )

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
        self.setAnonymous( True )

        storage = self.lib2.getStorage( )
        # add True
        link = urlbilder( 'action', self.lib2.id, "add", p='', n='new dir' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'created' in [m.message for m in list( resp.context['messages'] )][0]
        storage.remove( FilePath.join( '', 'new dir' ) )
        # delete False
        link = urlbilder( 'action', self.lib2.id, "delete", p=u"Фото 007.bin" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # trash False
        link = urlbilder( 'action', self.lib2.id, "trash", p=u"Фото 007.bin" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # rename False
        link = urlbilder( 'action', self.lib2.id, "rename", p=u"Фото 007.bin", n='Фото070.jpg' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # move False
        link = urlbilder( 'action', self.lib2.id, "move", p=u"Фото 007.bin", n='/' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # link True
        link = urlbilder( 'action', self.lib2.id, "link", p=u"Фото 007.bin" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'link' in [m.message for m in list( resp.context['messages'] )][0]
        # zip False
        link = urlbilder( 'action', self.lib2.id, "zip", p=u"Фото 007.bin" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert resp.context['messages'].__len__( ) == 1
        assert 'You have no permission' in [m.message for m in list( resp.context['messages'] )][0]
        # size very simple dir test
        link = urlbilder( 'action', self.lib2.id, "size", p='docs' )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        size = filesizeformat( storage.size( 'docs', dir=True, cached=False ) )
        assert size == resp.content.strip( )

    def test_Path_Arr(self):
        """
        Test ``class="breadcrumbs"`` in html or ``patharr`` in template interpretation.

        The order is not important because we already check it in ``CodeTest.test_split_path``
        """
        self.client.login( username='admin', password='root' )

        link = urlbilder( 'browser', self.lib2.id, p='limited/core/templatetags' )
        resp = self.client.get( link )

        assert resp.status_code == 200
        assert '<a href="/">#Home</a>' in resp.content
        assert '<a href="/lib1/">FileManager</a>' in resp.content
        assert '<a href="/lib1/?p=limited">limited</a>' in resp.content
        assert 'templatetags' in resp.content

    def test_Download(self):
        """
        Test response of download page
        """
        self.client.login( username='B7W', password='root' )

        link = urlbilder( u'download', self.lib.id, p=u'No Folder' )
        resp = self.client.get( link )
        assert resp.status_code == 200
        assert escape( u"No file or directory find" ) in unicode( resp.content, errors='ignore' )

        link = urlbilder( u'download', self.lib.id, p=u'content.txt' )
        resp = self.client.get( link )
        assert resp.status_code == 200

        link = urlbilder( u'download', self.lib.id, p=u'Test Folder' )
        resp = self.client.get( link )
        assert resp.status_code == 200

        link = urlbilder( u'link', u"no_such_hash" )
        resp = self.client.get( link )
        assert resp.status_code == 200
        assert escape( u"such object does not exists or link is out of time" ) in unicode( resp.content, errors='ignore' )

        hash = Link.objects.get( id=1 ).hash
        link = urlbilder( 'link', hash )
        resp = self.client.get( link )
        assert resp.status_code == 200

        Link.objects.filter( id=1 ).update( path="No File" )
        hash = Link.objects.get( id=1 ).hash
        link = urlbilder( 'link', hash )
        resp = self.client.get( link )
        assert resp.status_code == 200
        assert escape( u"No file or directory find" ) in unicode( resp.content, errors='ignore' )
