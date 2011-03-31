# Create your views here.
import tempfile
import zipfile

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main.storage import FileStorage
from main.models import MHome
from main.controls import get_user, get_params
from main.utils import get_path_array

import logging


logger = logging.getLogger( __name__ )


def Index( request ):
    user = get_user( request )
    if not user:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    FileLibs = MHome.objects.select_related( 'lib' ).filter( user=user )

    return render( request, "index.html",
                   {
                       'FileLibs': FileLibs,
                       } )


@csrf_exempt
def Browser( request ):
    user = get_user( request )
    if not user:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    home_id, path = get_params( request )
    logger.debug( 'Br: ' + path )
    FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=home_id )

    patharr = get_path_array( path )

    Storage = FileStorage( FileLib.lib.path )
    files = Storage.listdir( path )

    if request.method == 'POST':
        logger.debug( str( request.FILES ) )
        logger.debug( str( request.FILES.getlist( 'files' ) ) )
        user = get_user( request )

        lib_id = request.POST['lib_id']
        path = request.POST['path']

        FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=lib_id )
        Storage = FileStorage( FileLib.lib.path )

        for file in request.FILES.getlist( 'files' ):
            name = file.name
            fool_path = Storage.path.join( path, name )
            Storage.save( fool_path, file )

    return render( request, "browser.html",
                   {
                       'path': path,
                       'patharr': patharr,
                       'home_id': home_id,
                       'home': FileLib.lib.name,
                       'files': files,
                       } )


@csrf_exempt
def Upload( request ):
    if request.method == 'POST':
        user = get_user( request )

        lib_id = request.POST['lib_id']
        path = request.POST['path']

        FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=lib_id )
        Storage = FileStorage( FileLib.lib.path )

        for filename, file in request.FILES.iteritems( ):
            name = request.FILES[filename].name
            fool_path = Storage.path.join( path, name )
            Storage.save( fool_path, file )

        #        for file in request.FILES:
        #            fool_path = Storage.path.join( path, file.name )
        #            Storage.save( fool_path, file )
        return HttpResponse( )


def Download( request ):
    if request.method == 'GET':
        user = get_user( request )
        if not user:
            return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

        home, path = get_params( request )

        FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=home )

        Storage = FileStorage( FileLib.lib.path )

        if Storage.isfile( path ):
            #wrapper = FileWrapper( Storage.open( path ) )
            response = HttpResponse( Storage.open( path ).read( ), content_type='application/force-download' )
            response['Content-Disposition'] = 'attachment; filename=%s' % Storage.path.name( path )
            response['Content-Length'] = Storage.size( path )

        if Storage.isdir( path ):
            temp = tempfile.TemporaryFile( )
            archive = zipfile.ZipFile( temp, 'w', zipfile.ZIP_DEFLATED )
            for abspath, name in Storage.listfiles( path ).items( ):
                archive.write( abspath, name )
            archive.close( )
            temp.seek( 0 )
            #wrapper = FileWrapper(temp)
            response = HttpResponse( temp.read( ), content_type='application/zip' )
            response['Content-Disposition'] = 'attachment; filename=%s.zip' % Storage.path.name( path )
            response['Content-Length'] = temp.tell( )

        return response
