import os
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote


class HttpResponseReload( HttpResponse ):
    status_code = 302

    def __init__(self, request):
        HttpResponse.__init__( self )
        referer = request.META.get( 'HTTP_REFERER' )
        self['Location'] = iri_to_uri( referer or "/" )



def split_path( path ):
    """
    Split path for folders name
    with path fot this name

    Example::

        /root/path1/path2 ->
        root:/root, path1:/root/path2, path2:/root/path1/path2
    """
    def __split_path( path, data ):
        name = os.path.basename( path )
        if name != '':
            newpath = os.path.dirname( path )
            data = __split_path( newpath, data )
            data.append( (name, path) )
            return data
        return data

    return __split_path( path, [] )


def LoadPermissions( using=None ):
    """
    Enumerate and create all permissions
    For any count of columns in MPermission
    """
    from limited.models import MPermission

    fields = MPermission.fields()
    count = len( fields )
    last = count - 1
    rng = range( count )
    data = [0 for x in rng]

    for i in range( 2 ** count ):
        Pemm = MPermission( )
        for l in range( count ):
            setattr( Pemm, fields[l], data[l] )
        Pemm.save( using=using )

        data[last] += 1
        for j in reversed( rng ):
            if data[j] == 2:
                data[j] = 0
                data[j - 1] += 1


def UrlParametrs( **kwargs ):
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
        str += '%s=%s' % (key, urlquote( val ))

    return str
