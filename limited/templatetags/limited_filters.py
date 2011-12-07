# -*- coding: utf-8 -*-

import re

from django import template
from limited.controls import truncate_path

register = template.Library( )


@register.filter
def truncatepath( value, arg=None ):
    """
    Minimize/truncate file path. Can cut extensions or not.
    
    * arg:  "int.(ext|noext)"
    * arg:  "(ext|noext)"
    * arg:  "int"
    """
    if arg != None:
        len, ext = re.match( r"^(\d+)?\.?(\w+)?$", arg ).groups( )
        if len != None and ext != None:
            if ext == "ext":
                return truncate_path( value, length=int( len ), ext=True )
            elif ext == "noext":
                return truncate_path( value, length=int( len ), ext=False )
        elif len != None:
            return truncate_path( value, length=int( len ) )
        elif ext != None:
            if ext == "ext":
                return truncate_path( value, ext=True )
            elif ext == "noext":
                return truncate_path( value, ext=False )
    return truncate_path( value )


@register.tag
def joinpath(parser, token):
    """
    Join paths by '/', without adding first '/'.
    can save result in variable in such way ``as name``

    Sample usage::
    
        {% joinpath "/" item.path item.name as path %}
        {{ path|truncatepath }}
    """
    args = token.split_contents( )[1:]
    if len( args ) > 3:
        if args[-2] == u"as":
            return JoinPathNode( args[0:-2], args[-1] )

    return JoinPathNode( args )


class JoinPathNode( template.Node ):
    """
    ``Template.Node`` class for ``joinpath`` tag
    """

    def __init__(self, args, asvar=None ):
        self.args = [template.Variable( x ) for x in args]
        self.asvar = asvar

    def render(self, context):
        path = ""
        for item in self.args:
            str = item.resolve( context )
            if str:
                if str.startswith( '/' ):
                    path += str
                else:
                    path += '/' + str
        if path.startswith( '/' ):
            path = path[1:]
        if self.asvar != None:
            context[self.asvar] = path
            return ''
        return path
