import logging
import re
import tempfile
import zipfile
from django.conf import settings
from django.contrib.auth.models import User
from django.core.servers.basehttp import FileWrapper
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.utils.encoding import smart_str

from limited.models import MHome, MFileLib, MPermission
from limited.storage import FileStorage


def isUserCanView( user ):
    """
    If user can view or need login
    """
    if user.is_authenticated( ):
        return True
    elif user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return True
    return False


def getHome( user, lib_id ):
    """
    Get MHome plus related FileLib
    depending on is_authenticated or not
    and LIMITED_ANONYMOUS
    """
    if user.is_authenticated( ):
        if user.is_superuser:
            home = MHome()
            home.lib = MFileLib.objects.get( id=lib_id )
            home.permission = MPermission.Full()
            return home
        elif settings.LIMITED_ANONYMOUS:
            home = MHome.objects.select_related( 'lib', 'permission' ).\
                filter(Q(user=user) | Q(user=settings.LIMITED_ANONYMOUS_ID), lib__id=lib_id)
            length = len(home)
            if length == 0:
                raise MHome.DoesNotExist
            # if len==2 than we have Anon and User permission
            # so we need to get User once
            elif length == 2:
                if home[0].user_id == settings.LIMITED_ANONYMOUS_ID:
                    return home[1]
                # else: return home[0]
            return home[0]
        else:
            return MHome.objects.select_related( 'lib', 'permission' ).get( user=user, lib__id=lib_id )

    elif user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return MHome.objects.select_related( 'lib' ).get( user=settings.LIMITED_ANONYMOUS_ID, lib__id=lib_id )


def getHomes( user ):
    """
    Get MHome plus related FileLib
    depending on is_authenticated or not
    and LIMITED_ANONYMOUS
    """
    if user.is_authenticated( ):
        if user.is_superuser:
            homes = []
            libs = MFileLib.objects.all( ).distinct( )
            for item in libs:
                homes.append( MHome( lib=item ) )
            return homes
        else:
            return MHome.objects.select_related( 'lib' ).filter( user=user )
    elif user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return MHome.objects.select_related( 'lib' ).filter( user=settings.LIMITED_ANONYMOUS_ID )


def getUser( user ):
    """
    Return normal User obj for anon
    """
    if user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return User.objects.get( id=settings.LIMITED_ANONYMOUS_ID )
    return user


def Downloads( home, path ):
    """
    Return HttpResponse obj
    with file attachment
    or zip temp folder attachment
    """
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


def truncate_path( str, length=64, ext=False):
    """
    Truncate long path. if ext=True the path extensions will not deleted

    long name.ext -> {length}...ext
    or if fail long name - {length}..
    """
    if ext == True:
        restr = r"^(.{%s}).*\.(\w+)$" % length
        name_ext = re.match( restr, str )
        if name_ext != None:
            #return "%s..%s" % name_ext.groups( )
            filename = name_ext.group(1).strip()
            fileext = name_ext.group(2).strip()
            return "{0}..{1}".format( filename, fileext )
    if len(str) < length:
        return str
    else:
        return str[:length].strip() + ".."
