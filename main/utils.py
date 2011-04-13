import os
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri


class HttpResponseReload( HttpResponse ):
    status_code = 302

    def __init__(self, request):
        HttpResponse.__init__( self )
        referer = request.META.get( 'HTTP_REFERER' )
        self['Location'] = iri_to_uri( referer or "/" )


# Split path for folders name
# with path fot this name
#   example: /root/path1/path2
#       root:/root, path1:/root/path2, path2:/root/path1/path2
def split_path( path ):
    def __split_path( path, data ):
        name = os.path.basename( path )
        if name != '':
            newpath = os.path.dirname( path )
            data = __split_path( newpath, data )
            data.append( (name, path) )
            return data
        return data

    return __split_path( path, [] )

# Enumerate and create all permissions
# For any count of columns in MPermission
def LoadPermissions():
    from main.models import MPermission

    fields = MPermission.fields()
    count = len( fields )
    last = count - 1
    rng = range( count )
    data = [0 for x in rng]

    for i in range( 2 ** count ):
        print i, data
        Pemm = MPermission( )
        for l in range( count ):
            setattr( Pemm, fields[l], data[l] )
            print '. . .', fields[l], data[l]
        Pemm.save( )

        data[last] += 1
        for j in reversed( rng ):
            if data[j] == 2:
                data[j] = 0
                data[j - 1] += 1


def UrlGET( **kwargs ):
    str = None
    for key,val in kwargs.items():
        if not str: str = '?'
        else: str += '&amp;'
        str += '%s=%s' % (key,val)

    return str
