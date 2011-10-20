# -*- coding: utf-8 -*-

from StringIO import StringIO
from PIL import Image

from django.core.files.base import ContentFile

class ResizeImage:
    def __init__(self, filein):
        self.file = Image.open( filein )
        if self.file.mode not in ('L', 'RGB'):
            self.file = self.file.convert( 'RGB' )
        self.quality = 95
        self.type = "JPEG"

    @property
    def width(self):
        return self.file.size[0]

    @property
    def height(self):
        return self.file.size[1]

    def resize(self, width, height):
        self.file = self.file.resize( (width, height), Image.ANTIALIAS )

    def crop(self, x_offset, y_offset, width, height ):
        self.file = self.file.crop( (x_offset, y_offset, width, height) )

    def cropCenter(self, width, height):
        x_offset = ( self.width - width ) / 2
        y_offset = ( self.height - height ) / 2
        print x_offset, y_offset
        self.crop( x_offset, y_offset, x_offset + width, y_offset + height )

    def isPortrait(self):
        return self.width < self.height

    def isLandscape(self):
        return self.width >= self.height

    def isBigger(self, width, height):
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
        self.file.save( fileio, self.type, quality=self.quality )

