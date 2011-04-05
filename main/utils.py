import os
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri


class HttpResponseReload(HttpResponse):

    status_code = 302

    def __init__(self, request):
        HttpResponse.__init__(self)
        referer = request.META.get('HTTP_REFERER')
        self['Location'] = iri_to_uri(referer or "/")

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