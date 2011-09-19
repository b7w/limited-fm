# -*- coding: utf-8 -*-

from django.utils.html import escape

from limited import settings
from limited.files.storage import FilePath
from limited.tests.base import StorageTestCase
from limited.utils import urlbilder


class ActionTest( StorageTestCase ):
    """
    Test Action api that need pre and post features
    """

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
        assert self.storage.exists( u"Test Folder/content[1].txt" ) == True
        assert self.storage.exists( u"Test Folder/Фото 007.bin" ) == True
        assert self.storage.exists( u"Test Folder/content[2].txt" ) == True

    def test_Clear(self):
        """
        Test ActionClear.

        test with not stuff user and with administrator
        """
        link_cache = urlbilder( u'clear', self.lib.id, u'cache' )
        link_trash = urlbilder( u'clear', self.lib.id, u'trash' )

        file_cache = FilePath.join( settings.LIMITED_CACHE_PATH, u"test.bin" )
        file_trash = FilePath.join( settings.LIMITED_TRASH_PATH, u"test.bin" )

        self.storage.create( file_cache, u"Test" )
        self.storage.create( file_trash, u"Test" )

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
