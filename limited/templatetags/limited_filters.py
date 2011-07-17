# -*- coding: utf-8 -*-
import re

from django import template
from limited.controls import MinimizeString

register = template.Library()

# Minimize file path
# arg "int.(ext|noext)"
# arg "(ext|noext)"
# arg "int"
@register.filter
def mini( value, arg=None ):
    if arg != None:
        len, ext = re.match( r"^(\d+)?\.?(\w+)?$", arg ).groups( )
        if len != None and ext != None:
            if ext == "ext":
                return MinimizeString( value, length=int( len ), ext=True )
            elif ext == "noext":
                return MinimizeString( value, length=int( len ), ext=False )
        elif len != None:
            return MinimizeString( value, length=int( len ) )
        elif ext != None:
            if ext == "ext":
                return MinimizeString( value, ext=True )
            elif ext == "noext":
                return MinimizeString( value, ext=False )
    return MinimizeString( value )


# join paths by '/'
# without adding first '/'
@register.tag
def joinpath(parser, token):
    args = token.split_contents( )[1:]
    return JoinPathNode(args)

# template.Node class for joinpath tag
class JoinPathNode( template.Node ):
    def __init__(self, args):
        self.args = [ template.Variable( x ) for x in args ]

    def render(self, context):
        path = ""
        for item in self.args:
            str = item.resolve(context)
            if str:
                if str.startswith('/'):
                    path += str
                else:
                    path += '/' + str
        if path.startswith('/'):
            path = path[1:]
        return path