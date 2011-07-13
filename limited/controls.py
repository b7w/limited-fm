import logging
import re
import tempfile
import zipfile
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.utils.encoding import smart_str

from limited.models import MHome
from limited.storage import FileStorage


# If user can view or need login
def isUserCanView( user ):
    if user.is_authenticated( ):
        return True
    elif user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return True
    return False


# Get MHome plus related FileLib
# depending on is_authenticated or not
# and LIMITED_ANONYMOUS
def getFileLib( user, home_id ):
    if user.is_authenticated( ):
        if settings.LIMITED_ANONYMOUS:
            return MHome.objects.select_related( 'lib' ).\
                filter(Q(user=user) | Q(user=settings.LIMITED_ANONYMOUS_ID), lib__id=home_id)[0]
        else:
            return MHome.objects.select_related( 'lib' ).get( user=user, lib__id=home_id )

    elif user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return MHome.objects.select_related( 'lib' ).get( user=settings.LIMITED_ANONYMOUS_ID, lib__id=home_id )


# Get MHome plus related FileLib
# depending on is_authenticated or not
# and LIMITED_ANONYMOUS
def getFileLibs( user ):
    if user.is_authenticated( ):
        return MHome.objects.select_related( 'lib' ).filter( user=user )
    elif user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return MHome.objects.select_related( 'lib' ).filter( user=settings.LIMITED_ANONYMOUS_ID )


# Return HttpResponse obj
# with file attachment
# or zip temp folder attachment
def Downloads( home, path ):
    File = FileStorage( home )
    response = None

    if File.isfile( path ):
        wrapper = FileWrapper( File.open( path ) )
        #wrapper = File.open( path ).read( )
        response = HttpResponse( wrapper, content_type='application/force-download' )
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str( File.path.name( path ) )
        response['Content-Length'] = File.size( path )

    elif File.isdir( path ):
        temp = tempfile.TemporaryFile( )
        archive = zipfile.ZipFile( temp, 'w', zipfile.ZIP_DEFLATED )
        dirname = File.path.name( path )
        for abspath, name in File.listfiles( path ).items( ):
            name = File.path.join( dirname, name )
            archive.write( abspath, name )

        archive.close( )
        wrapper = FileWrapper( temp )
        response = HttpResponse( wrapper, content_type='application/zip' )
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % smart_str( File.path.name( path ) )
        response['Content-Length'] = temp.tell( )
        temp.seek( 0 )

    return response


# Minimise long strings
#  long name.ext -> {length}...ext
#  or if fail long name - {length+2}
def MinimizeString( str, length=32, ext=False):
    if ext == True:
        restr = r"^(.{%s}).*\.(\w+)$" % length
        name_ext = re.match( restr, str )
        if name_ext != None:
            return "%s...%s" % name_ext.groups( )
    if len(str) < length + 2:
        return str
    else:
        return str[:length + 2] + "..."