# -*- coding: utf-8 -*-

from limited import settings
from limited.tests.base import StorageTestCase
from limited.utils import urlbilder

from lviewer.utils import ResizeOptions, ResizeImage


class ViewerTest( StorageTestCase ):
    def setUp(self):
        """
        Add variables to resource fantasy-world.jpeg, big image size.
        Copy fantasy-world.jpeg to lib test, Test Folder.
        """
        super( ViewerTest, self ).setUp( )

        self.image_fantasy_world = u"lviewer/tests/resources/fantasy-world.jpeg"
        self.set_width = settings.LVIEWER_BIG_IMAGE['WIDTH']
        self.set_height = settings.LVIEWER_BIG_IMAGE['HEIGHT']
        filein = self.storage2.open( self.image_fantasy_world, mode='rb', signal=False )
        self.storage.save( u"Test Folder/fantasy-world.jpeg", filein, signal=False )
        filein.close( )

    def test_ResizeOptions(self):
        """
        Test ResizeOptions class
        """
        opt1 = ResizeOptions( { 'WIDTH': 300, 'HEIGHT': 200, 'CROP': True, } )
        assert opt1.width == 300
        assert opt1.height == 200
        assert opt1.size == 300
        assert opt1.crop == True
        opt2 = ResizeOptions( { 'WIDTH': 300, 'HEIGHT': 200, } )
        assert opt2.crop == False
        opt3 = ResizeOptions( "1280x720" )
        assert opt3.width == 1280
        assert opt3.height == 720
        assert opt3.crop == False
        opt4 = ResizeOptions( "1280x720xC" )
        assert opt4.width == 1280
        assert opt4.height == 720
        assert opt4.crop == True

    def test_ResizeImage(self):
        """
        Test ResizeImage class
        except saveTo method
        """
        try:
            filein = self.storage2.open( self.image_fantasy_world, mode='rb', signal=False )
            newImage = ResizeImage( filein )

            assert newImage.width == 3840
            assert newImage.height == 2000
            assert newImage.isBigger( self.set_width, self.set_height ) == False
            assert newImage.isPortrait( ) == False
            assert newImage.isLandscape( ) == True
            assert newImage.minSize( 1000 ) == (1920, 1000)
            assert newImage.maxSize( 1000 ) == (1000, 520)
            newImage.resize( 1000, 520 )
            assert newImage.width == 1000
            assert newImage.height == 520
            newImage.cropCenter( 780, 520 )
            assert newImage.width == 780
            assert newImage.height == 520
        finally:
            filein.close( )

    def test_ResizeView(self):
        """
        Test status code of resize view
        """
        link = urlbilder( u'resize', self.lib.id, u"1280x720", p=u"Test Folder/fantasy-world.jpeg" )
        resp = self.client.get( link, follow=True )
        assert resp.status_code == 200
