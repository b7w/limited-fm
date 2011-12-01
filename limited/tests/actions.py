# -*- coding: utf-8 -*-

from django.utils.html import escape

from limited import settings
from limited.files.storage import FilePath
from limited.models import History
from limited.tests.base import StorageTestCase
from limited.utils import urlbilder


class ActionTest( StorageTestCase ):
    """
    Test Action api that need pre and post features
    """

    def getLastHistory(self):
        return History.objects.order_by( '-pk' )[0]

    def test_Upload(self):
        """
        Test Upload files
        """
        file1 = self.storage.open( u"content.txt" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [file1] } )
        file1.close( )
        assert self.storage.exists( u"Test Folder/content.txt" ) == False

        self.client.login( username='B7W', password='root' )
        file1 = self.storage.open( u"content.txt" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [file1] } )
        file1.close( )
        assert self.storage.exists( u"Test Folder/content.txt" ) == True

        file1 = self.storage.open( u"content.txt" )
        file2 = self.storage.open( u"Фото 007.bin" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [file1, file2, file1] } )
        file1.close( )
        file2.close( )
        assert self.storage.exists( u"Test Folder/content.txt" ) == True
        assert self.storage.exists( u"Test Folder/Фото 007.bin" ) == True
        assert self.storage.exists( u"Test Folder/content.txt" ) == True

        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [] } )
        his = self.getLastHistory( )
        assert len( his.files ) == 3
        assert his.files[0] == u"content.txt"
        assert his.files[1] == u"Фото 007.bin"
        assert his.files[2] == u"content.txt"

    def test_Upload_Files_Allowed(self):
        """
        Test settings.LIMITED_FILES_ALLOWED
        """
        settings.LIMITED_ANONYMOUS = True
        file0 = self.storage.open( u"content.txt" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [file0] } )
        file0.close( )
        assert self.storage.exists( u"Test Folder/content.txt" ) == False

        self.client.login( username='B7W', password='root' )
        self.storage.extra.create( u"test.rar", "XXX" * 2 ** 4 )
        file1 = self.storage.open( u"test.rar" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [file1] } )
        file1.close( )
        assert self.storage.exists( u"Test Folder/test.rar" ) == False

        settings.LIMITED_FILES_ALLOWED['ONLY'] = ['txt']
        file2 = self.storage.open( u"Фото 007.bin" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [file2] } )
        file2.close( )
        assert self.storage.exists( u"Test Folder/Фото 007.bin" ) == False

        file3 = self.storage.open( u"content.txt" )
        self.client.post( urlbilder( u'upload', self.lib.id ), { 'p': 'Test Folder', 'files': [file3] } )
        file3.close( )
        assert self.storage.exists( u"Test Folder/content.txt" ) == True

    def test_Clear(self):
        """
        Test ActionClear.

        test with not stuff user and with administrator
        """
        link_cache = urlbilder( u'clear', self.lib.id, u'cache' )
        link_trash = urlbilder( u'clear', self.lib.id, u'trash' )

        file_cache = FilePath.join( settings.LIMITED_CACHE_PATH, u"test.bin" )
        file_trash = FilePath.join( settings.LIMITED_TRASH_PATH, u"test.bin" )

        self.storage.extra.create( file_cache, u"Test" )
        self.storage.extra.create( file_trash, u"Test" )

        self.client.login( username='B7W', password='root' )

        resp = self.client.get( link_cache, follow=True )
        assert resp.status_code == 200
        assert escape( u"You have no permission to clear cache" ) in unicode( resp.content, errors='ignore' )
        assert self.storage.exists( file_cache ) == True

        resp = self.client.get( link_trash, follow=True )
        assert resp.status_code == 200
        assert escape( u"You have no permission to clear trash" ) in unicode( resp.content, errors='ignore' )
        assert self.storage.exists( file_trash ) == True

        self.client.login( username='admin', password='root' )

        resp = self.client.get( link_cache )
        assert resp.status_code == 302
        assert self.storage.exists( file_cache ) == False

        resp = self.client.get( link_trash )
        assert resp.status_code == 302
        assert self.storage.exists( file_trash ) == False

    def test_Add(self):
        """
        Test action add.
		Create directory and upload file.
        """
        url = u"http://www.google.ru/images/srpr/logo3w.png"
        link_mkdir = urlbilder( 'action', self.lib.id, 'add', n='New dir', p='' )
        link_url = urlbilder( 'action', self.lib.id, 'add', n=url, p='' )

        self.client.login( username='B7W', password='root' )

        resp = self.client.get( link_mkdir, follow=True )
        assert resp.status_code == 200
        assert self.storage.exists( u"New dir" ) == True

        resp = self.client.get( link_url, follow=True )
        assert resp.status_code == 200
        self.timer.sleep( )
        assert self.storage.exists( u"logo3w.png" ) == True

    def test_Chroot(self):
        """
        Test to inject in path something like that '../'
        """
        self.client.login( username='B7W', password='root' )
        for item in ['../', 'Test Folder/../../', '/', '/home', ]:
            link = urlbilder( 'browser', self.lib.id, p=item )
            resp = self.client.get( link, follow=True )
            assert resp.status_code == 200
            assert "IOError" in resp.content, link