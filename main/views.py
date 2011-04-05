# -*- coding: utf-8 -*-
# Create your views here.
import tempfile
import zipfile
import json

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main.storage import FileStorage, StorageError
from main.models import MHome
from main.controls import get_user, get_params
from main.utils import get_path_array, split_path

from django.utils.log import logger

def Index( request ):
    user = get_user( request )
    logger.info( 'Index page test' )
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

    logger.info( path )
    patharr = split_path( path )

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


def Action( request, command ):
    out = { 'error': False, 'message': "Warn. Only ajax allowed to '%s'" % command }
    home = request.POST['home']
    path = request.POST['path']

    user = get_user( request )
    FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=home )
    Storage = FileStorage( FileLib.lib.path )

    if request.is_ajax( ):
        if command == 'delete':
            try:
                Storage.totrash( path )
                out['message'] = "'%s' successfully moved to trash" % Storage.path.name( path )
            except Exception as e:
                out['error'] = True
                out['message'] = e.message

        if command == 'rename':
            try:
                name = request.POST['name']
                Storage.rename( path, name )
                out['message'] = "'%s' successfully rename to '%s'" % (Storage.path.name( path ), name)
            except StorageError as e:
                out['error'] = True
                out['message'] = e.message

    return HttpResponse( json.dumps( out ) )

def Act( request, command ):
    home = request.GET['h']
    path = request.GET['p']

    user = get_user( request )
    FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=home )
    Storage = FileStorage( FileLib.lib.path )

    if command == 'delete':
        try:
            Storage.totrash( path )
            messages.success( request, "'%s' successfully moved to trash" % Storage.path.name( path ) )
        except Exception as e:
            messages.error( request, e.message )

    elif command == 'rename':
        try:
            name = request.GET['n']
            Storage.rename( path, name )
            messages.success( request, "'%s' successfully rename to '%s'" % (Storage.path.name( path ), name) )
        except StorageError as e:
            messages.error( request, e.message )

    elif command == 'move':
        try:
            path2 = request.GET['p2']
            Storage.move( path, path2 )
            messages.success( request, "'%s' successfully moved to '%s'" %  (Storage.path.name( path ), path2) )
        except StorageError as e:
            messages.error( request, e.message )

    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))


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

        return HttpResponse( )


def Download( request ):
    if request.method == 'GET':
        user = get_user( request )
        if not user:
            return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

        home, path = get_params( request )

        FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=home )

        Storage = FileStorage( FileLib.lib.path )
        logger.debug( path )
        if Storage.isfile( path ):
            #wrapper = FileWrapper( Storage.open( path ) )
            response = HttpResponse( Storage.open( path ).read( ), content_type='application/force-download' )
            response['Content-Disposition'] = 'attachment; filename=%s' % Storage.path.name( path )
            response['Content-Length'] = Storage.size( path )

        elif Storage.isdir( path ):
            temp = tempfile.TemporaryFile( )
            archive = zipfile.ZipFile( temp, 'w', zipfile.ZIP_DEFLATED )
            dirname = Storage.path.name( path )
            for abspath, name in Storage.listfiles( path ).items( ):
                name = Storage.path.join( dirname, name )
                archive.write( abspath, name )

            archive.close( )
            temp.seek( 0 )
            #wrapper = FileWrapper(temp)
            response = HttpResponse( temp.read( ), content_type='application/zip' )
            response['Content-Disposition'] = 'attachment; filename=%s.zip' % Storage.path.name( path ).encode(
                'latin-1', 'replace' )
            response['Content-Length'] = temp.tell( )

        else:
            raise Http404( 'No file or directory find' )

        return response
