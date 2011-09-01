# -*- coding: utf-8 -*-

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