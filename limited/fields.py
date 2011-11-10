# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.forms.widgets import Textarea
from django.utils import simplejson

from limited.utils import TreeNode

logger = logging.getLogger( __name__ )

class JsonTreeField( models.TextField ):
    """
    A simple JSON filed. Store text in database and TreeNode in python.
    """
    __metaclass__ = models.SubfieldBase

    description = "Json Tree object"

    def formfield(self, **kwargs):
        kwargs['widget'] = JSONWidget( attrs={ 'class': 'vLargeTextField' } )
        return super( JsonTreeField, self ).formfield( **kwargs )

    def get_db_prep_value(self, value, connection, prepared=False):
        if value == '' or value == None:
            return None
        if isinstance( value, basestring ):
            return value
        return simplejson.dumps( value.toDict( ) )

    def to_python(self, value):
        if value == '' or value == None:
            return TreeNode( "root", "" )
        if not isinstance( value, basestring ):
            return value
        DictData = simplejson.loads( value )
        return TreeNode.build( DictData )


class JSONWidget( Textarea ):
    """
    Prettify dumps of all non-string JSON data.
    """

    def render(self, name, value, attrs=None):
        if not isinstance( value, basestring ) and value is not None:
            value = simplejson.dumps( value.toDict( ), indent=4, sort_keys=True )
        return super( JSONWidget, self ).render( name, value, attrs )


class TextListField( models.CharField ):
    """
    A simple comma separated CharField filed. Store text in database and list in python.
    """
    __metaclass__ = models.SubfieldBase

    description = "Comma separated object"

    def get_db_prep_value(self, value, connection, prepared=False):
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