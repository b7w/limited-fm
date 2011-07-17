# -*- coding: utf-8 -*-
import logging
import re
from django import template
from limited.controls import MinimizeString

register = template.Library()

# Minimize file path
# arg "int.(ext|noext)"
# arg "(ext|noext)"
# arg "int"
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

register.filter('mini', mini)

def upperfirst( value ):
    return