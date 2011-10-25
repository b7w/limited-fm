# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.utils import simplejson

from limited.utils import TreeNode

logger = logging.getLogger( __name__ )

class JsonTreeField( models.TextField ):
    """
    A simple JSON filed. Store text in database and TreeNode in python.
    """
    __metaclass__ = models.SubfieldBase

    description = "Json Tree object"

    def get_db_prep_value(self, value):
        if value == '' or value == None:
            return None
        json = value.toDict( )
        return simplejson.dumps( json )

    def to_python(self, value):
        if value == '' or value == None:
            return TreeNode( "root", "" )
        if not isinstance( value, basestring ):
            return value
        DictData = simplejson.loads( value )
        return TreeNode.build( DictData )


class TextListField( models.CharField ):
    """
    A simple comma separated CharField filed. Store text in database and list in python.
    """
    __metaclass__ = models.SubfieldBase

    description = "Comma separated object"

    def get_db_prep_value(self, value):
        """
        Truncate list if his items in sum greater than ``max_length``.
        And log this error.
        """
        if value == '' or value == None:
            return None
        tmp = 0
        val = []
        for item in value:
            tmp += len( item ) + 1
            if tmp <= self.max_length:
                val.append( item )
            else:
                break

        if len( val ) != len( value ):
            logger.error( "TextListField. Array was truncated - {0}".format( value ) )
        return ';'.join( val )

    def to_python(self, value):
        if value == '' or value == None:
            return []
        if not isinstance( value, basestring ):
            return value
        return value.split( ';' )