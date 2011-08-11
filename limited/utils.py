# -*- coding: utf-8 -*-

import os
import urllib

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri
from django.utils.datastructures import SortedDict
from django.utils.http import urlquote


class HttpResponseReload( HttpResponse ):
    status_code = 302

    def __init__(self, request):
        HttpResponse.__init__( self )
        referer = request.META.get( u"HTTP_REFERER" )
        self[u"Location"] = iri_to_uri( referer or "/" )


class Singleton( type ):
    def __init__(cls, name, bases, dict):
        super( Singleton, cls ).__init__( name, bases, dict )
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super( Singleton, cls ).__call__( *args, **kw )
            return cls.instance


def split_path( path ):
    """
    Split path for folders name
    with path fot this name

    Example::

        /root/path1/path2 ->
        root:/root, path1:/root/path2, path2:/root/path1/path2
    """
    def _split_path( path, data ):
        name = os.path.basename( path )
        if name != '':
            newpath = os.path.dirname( path )
            data = _split_path( newpath, data )
            data[name] = path
            return data
        return data

    return _split_path( path, SortedDict() )


def load_permissions( using=None ):
    """
    Enumerate and create all permissions
    For any count of columns in Permission
    """
    from limited.models import Permission

    fields = Permission.fields()
    count = len( fields )
    last = count - 1
    rng = range( count )
    data = [0 for x in rng]

    for i in range( 2 ** count ):
        Pemm = Permission( )
        for l in range( count ):
            setattr( Pemm, fields[l], data[l] )
        Pemm.save( using=using )

        data[last] += 1
        for j in reversed( rng ):
            if data[j] == 2:
                data[j] = 0
                data[j - 1] += 1


def url_params( **kwargs ):
    """
    Create string with http params

    Sample usage::

        from id=1,name='user',..
        to   ?id=1&name=user
    """
    str = None
    for key, val in kwargs.items( ):
        if not str: str = '?'
        else: str += '&'
        str += u"%s=%s" % (key, urlquote( val ))

    return str


def urlbilder( name, *args, **kwargs ):
    """
    Create link with http params

    Sample usage::

        from name,id=1,name='user',..
        to   /url/name/../?id=1&name=user
    """
    if kwargs:
        return reverse( name, args=args ) + url_params( **kwargs )
    else:
        return reverse( name, args=args )


def url_get_filename( url ):
    """
    Get tail without ?,=,& and try it to decode to utf-8
    or get domain name if break
    """
    result = ''
    try:
        url = iri_to_uri( url )
        # convert to acii cose urllib is shit
        bits = str( url ).split( '/' )
        names = [x for x in bits if x != '']
        # delete none useful chars
        for ch in names[-1]:
            if ch not in ('?', '=', '&',):
                result += ch
        result = urllib.url2pathname( result ).decode( 'utf-8' )

    except Exception as e:
        # set name as domen
        result = url.split( '/' )[1]

    return result