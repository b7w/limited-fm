import tempfile
import zipfile
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse

from limited.models import MHome

# Get authenticated user
# or anonymous user if he had any FileLibs
# or None
from limited.storage import FileStorage

def get_user( request ):
    if request.user.is_authenticated( ):
        return request.user

    elif request.user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        Anonymous = User.objects.get( username__exact='Anonymous' )
        return Anonymous


# return GET params
# 'h' or Http404 and 'p' or ''
# from request obj
def get_params( request ):
    if 'h' in request.GET:
        home = int( request.GET['h'] )
    else:
        raise Http404( 'Bag http request' )

    if 'p' in request.GET:
        path = request.GET['p']
    else:
        path = ''

    return ( home, path )


# Return HttpResponse obj
# with file attachment
# or zip temp folder attachment
def Downloads( home, path ):
    File = FileStorage( home )
    response = None

    if File.isfile( path ):
        #wrapper = FileWrapper( Storage.open( path ) )
        response = HttpResponse( File.open( path ).read( ), content_type='application/force-download' )
        response['Content-Disposition'] = 'attachment; filename=%s' % File.path.name( path )
        response['Content-Length'] = File.size( path )

    elif File.isdir( path ):
        temp = tempfile.TemporaryFile( )
        archive = zipfile.ZipFile( temp, 'w', zipfile.ZIP_DEFLATED )
        dirname = File.path.name( path )
        for abspath, name in File.listfiles( path ).items( ):
            name = File.path.join( dirname, name )
            archive.write( abspath, name )

        archive.close( )
        temp.seek( 0 )
        #wrapper = FileWrapper(temp)
        response = HttpResponse( temp.read( ), content_type='application/zip' )
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % File.path.name( path ).encode(
            'latin-1', 'replace' )
        response['Content-Length'] = temp.tell( )

    return response