# -*- coding: utf-8 -*-
from django.utils.html import escape

from limited.core import settings
from limited.core.tests.base import StorageTestCase
from limited.core.utils import urlbilder


class ViewerTest( StorageTestCase ):
    def setUp(self):
        """
        Add variables to resource fantasy-world.jpeg, big image size.
        Copy fantasy-world.jpeg to lib test, Test Folder.
        """
        super( ViewerTest, self ).setUp( )

        self.image_fantasy_world = u"limited/lviewer/tests/resources/fantasy-world.jpeg"
        self.set_width = settings.LVIEWER_BIG_IMAGE['WIDTH']
        self.set_height = settings.LVIEWER_BIG_IMAGE['HEIGHT']
        filein = self.storage2.open( self.image_fantasy_world, mode='rb', signal=False )
        self.storage.save( u"Test Folder/fantasy-world.jpeg", filein, signal=False )
        self.storage.save( u"Test Folder/fantasy-world2.jpeg", filein, signal=False )
        filein.close( )

    def test_LinkToGallery(self):
        """
        Test status code of resize view
        """
        assert self.client.login( username='B7W', password='root' )

        link = urlbilder( 'browser', self.lib.id, p='Test Folder' )
        resp = self.client.get( link, follow=True )

        assert resp.status_code == 200
        assert escape( u"View in a gallery" ) in unicode( resp.content, errors='ignore' )

    def test_ResizeView(self):
        """
        Test status code of reisze view with login and not
        """
        link = urlbilder( u'resize', self.lib.id, u"1280x720", p=u"Test Folder/fantasy-world.jpeg" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert escape( u"Login form" ) in unicode( resp.content, errors='ignore' )

        assert self.client.login( username='B7W', password='root' )
        link = urlbilder( u'resize', self.lib.id, u"1280x720", p=u"Test Folder/fantasy-world.jpeg" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200

        assert self.client.login( username='B7W', password='root' )
        link = urlbilder( u'resize', self.lib.id, u"200x200xC", p=u"Test Folder/fantasy-world.jpeg" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200

        # ResizeOptionsError
        assert self.client.login( username='B7W', password='root' )
        link = urlbilder( u'resize', self.lib.id, u"200d200xC", p=u"Test Folder/fantasy-world.jpeg" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 404

    def test_GalleryView(self):
        """
        Test status code of gallery with login and not
        """
        link = urlbilder( u'images', self.lib.id, p=u"Test Folder" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert escape( u"Login form" ) in unicode( resp.content, errors='ignore' )

        assert self.client.login( username='B7W', password='root' )
        link = urlbilder( u'images', self.lib.id, p=u"Test Folder" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200

    def test_PathHacks(self):
        """
        Test path hacks for chrooting
        """
        assert self.client.login( username='B7W', password='root' )

        link = urlbilder( u'images', self.lib.id, p=u"../" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert escape( u"IOError" ) in unicode( resp.content, errors='ignore' )

        link = urlbilder( u'resize', self.lib.id, u"1280x720", p=u"../fantasy-world.jpeg" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert escape( u"IOError" ) in unicode( resp.content, errors='ignore' )

    def test_WrongPaths(self):
        """
        Test path hacks for chrooting
        """
        assert self.client.login( username='B7W', password='root' )

        link = urlbilder( u'images', 5, p=u"Test Folder" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

        link = urlbilder( u'images', self.lib.id, p=u"NO Folder" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert escape( u"path 'NO Folder' doesn't exist or it isn't a directory" ) in unicode( resp.content, errors='ignore' )

        link = urlbilder( u'resize', 5, u"1280x720", p=u"fantasy-world.jpeg" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
        assert escape( u"No such file lib or you don't have permissions" ) in unicode( resp.content, errors='ignore' )

        link = urlbilder( u'resize', self.lib.id, u"1280x720", p=u"none.jpeg" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 404

        # file exists but not jpg|jpeg
        link = urlbilder( u'resize', self.lib.id, u"1280x720", p=u"content.txt" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 404

