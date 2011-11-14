# -*- coding: utf-8 -*-

import logging

from PIL import Image

logger = logging.getLogger( __name__ )

class ResizeImage:
    """
    Get file with image. Resize, crop it.
    """

    def __init__(self, filein):
        self.file = Image.open( filein )
        if self.file.mode not in ('L', 'RGB'):
            self.file = self.file.convert( 'RGB' )
        self.quality = 95
        self.type = "JPEG"

    @property
    def width(self):
        """
        Return image width
        """
        return self.file.size[0]

    @property
    def height(self):
        """
        Return image height
        """
        return self.file.size[1]

    def resize(self, width, height):
        """
        Resize image to ``width`` and ``width``
        """
        self.file = self.file.resize( (width, height), Image.ANTIALIAS )

    def crop(self, x_offset, y_offset, width, height ):
        """
        Crop image with ``x_offset``, ``y_offset``, ``width``, ``height``
        """
        self.file = self.file.crop( (x_offset, y_offset, width, height) )

    def cropCenter(self, width, height):
        """
        Cut out an image with ``width`` and ``height`` of the center
        """
        x_offset = ( self.width - width ) / 2
        y_offset = ( self.height - height ) / 2
        self.crop( x_offset, y_offset, x_offset + width, y_offset + height )

    def isPortrait(self):
        """
        Is width < height
        """
        return self.width < self.height

    def isLandscape(self):
        """
        Is width >= height
        """
        return self.width >= self.height

    def isBigger(self, width, height):
        """
        Is ``width`` and ``height`` bigger that this image
        """
        return width > self.width and height > self.height

    def minSize(self, value):
        """
        Scale images size where the min size len will be ``value``
        """
        if self.isLandscape( ):
            scale = float( self.height ) / value
            width = int( self.width / scale )
            return ( width, value )
        else:
            scale = float( self.width ) / value
            height = int( self.height / scale )
            return ( value, height )

    def maxSize(self, value):
        """
        Scale images size where the max size len will be ``value``
        """
        if self.isPortrait( ):
            scale = float( self.height ) / value
            width = int( self.width / scale )
            return ( width, value )
        else:
            scale = float( self.width ) / value
            height = int( self.height / scale )
            return ( value, height )

    def saveTo(self, fileio ):
        """
        Save to open file ``fileio``. Need to close by yourself.
        """
        self.file.save( fileio, self.type, quality=self.quality )


class ResizeOptionsError( Exception ):
    """
    Resize options error.
    """
    pass


class ResizeOptions:
    """
    Options for resize such as width, height,
    max size - max of width/height,
    crop - need or not.
    """

    def __init__(self, options):
        """
        Get sting with options or settings dict
        """
        self.width = 0
        self.height = 0
        self.size = 0
        self.crop = False
        if isinstance( options, dict ):
            self.setFromSetting( options )
        else:
            self.parse( options )

    def parse(self, string):
        """
        Do parsing. Executed in object init.
        """
        try:
            options = string.split( 'x' )
            self.width = int( options[0] )
            self.height = int( options[1] )
            self.size = max( self.width, self.height )
            self.crop = 'C' in options
        except Exception as e:
            logger.error( u"ResizeOptions. {0}. string:{1}".format( e, string ) )
            raise ResizeOptionsError( )

    def setFromSetting(self, value):
        """
        Set values from settings.IVIEWER_BIG_IMAGE for example
        """
        self.width = value['WIDTH']
        self.height = value['HEIGHT']
        self.size = max( self.width, self.height )
        self.crop = 'CROP' in value and value['CROP'] == True

    def toString(self):
        """
        Return string from witch then parametrs can be parsed in ``self.parse``
        """
        tmp = u"{0}x{1}".format( self.width, self.height )
        if self.crop:
            tmp += u"xC"
        return tmp