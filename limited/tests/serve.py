# -*- coding: utf-8 -*-

from limited import settings
from limited.serve.backends import BaseDownloadResponse
from limited.serve.manager import DownloadManager
from limited.tests.base import StorageTestCase


class DownloadManagerTest( StorageTestCase ):
    """
    Test DownloadManager
    """

    def setUp(self):
        """
        Add DownloadManager and set default settings
        """
        super( DownloadManagerTest, self ).setUp( )
        self.manager = DownloadManager( self.lib )
        settings.LIMITED_ZIP_HUGE_SIZE = 16 * 1024 * 1024
        settings.LIMITED_SERVE['BACKEND'] = 'limited.serve.backends.default'
        settings.LIMITED_SERVE['INTERNAL_URL'] = '/protected'

    def test_processing(self):
        """
        Test manager.is_need_processing and manager.process
        """
        settings.LIMITED_ZIP_HUGE_SIZE = 16 * 1024

        assert self.manager.is_need_processing( u"Test Folder" ) == False
        self.storage.extra.create( u"Test Folder/test.bin", "XXX" * 2 ** 16 )
        assert self.storage.size( u"Test Folder/test.bin" ) > 16 * 1024
        assert self.manager.is_need_processing( u"Test Folder" ) == True
        self.manager.process( u"Test Folder" )
        self.timer.sleep( )
        assert self.storage.exists( self.manager.cache_file( u"Test Folder" ) ) == True
        assert self.manager.is_need_processing( u"Test Folder" ) == False

    def test_processing_cache(self):
        """
        Test manager cache
        """
        settings.LIMITED_ZIP_HUGE_SIZE = 16 * 1024

        self.storage.extra.create( u"Test Folder/test.bin", "XXX" * 2 ** 4 )
        self.manager.process( u"Test Folder" )
        self.timer.sleep( )

        cache1 = self.manager.cache_file( u"Test Folder" )
        hash1 = self.lib.cache.hash
        assert self.storage.exists( cache1 ) == True

        self.storage.extra.create( u"Test Folder/test2.bin", "XXX" * 2 ** 4 )
        self.manager.cache = { }
        self.manager.process( u"Test Folder" )
        self.timer.sleep( )
        cache2 = self.manager.cache_file( u"Test Folder" )
        hash2 = self.lib.cache.hash

        assert self.storage.exists( cache1 ) == True
        assert self.storage.exists( cache2 ) == True
        assert hash1 != hash2

    def test_backend(self):
        """
        Test backend is isinstance of class BaseDownloadResponse
        """
        settings.LIMITED_SERVE['BACKEND'] = 'limited.serve.backends.nginx'
        backend = self.manager.get_backend( )
        assert isinstance( backend( None, { } ), BaseDownloadResponse ) == True

        settings.LIMITED_SERVE['BACKEND'] = 'limited.serve.backends.default'
        backend = self.manager.get_backend( )
        assert isinstance( backend( None, { } ), BaseDownloadResponse ) == True

    def test_response(self):
        """
        Test response Content-Disposition and len of content
        For nginx X-Accel-Redirect.
        """
        settings.LIMITED_SERVE['BACKEND'] = 'limited.serve.backends.nginx'
        response = self.manager.build( u"content.txt" )
        assert response['X-Accel-Redirect'] == u"/protected/%s/content.txt" % self.lib.path
        assert response['Content-Disposition'] == "attachment; filename=\"%s\"" % u"content.txt".encode( 'utf-8' )
        assert response.content.__len__( ) == 0

        settings.LIMITED_SERVE['BACKEND'] = 'limited.serve.backends.default'
        response = self.manager.build( u"content.txt" )
        assert response['Content-Disposition'] == "attachment; filename=\"%s\"" % u"content.txt".encode( 'utf-8' )
        assert response.content.__len__( ) != 0

        self.storage.extra.create( u"Test Folder/test.bin", "XXX" * 2 ** 4 )
        response = self.manager.build( u"Test Folder" )
        assert response['Content-Disposition'] == "attachment; filename=\"%s\"" % u"Test Folder.zip".encode( 'utf-8' )
        assert response.content.__len__( ) != 0