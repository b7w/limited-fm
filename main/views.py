# -*- coding: utf-8 -*-
# Create your views here.
import tempfile
import zipfile

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main.storage import FileStorage, StorageError
from main.models import MHome, MHistory, PermissionError
from main.controls import get_user, get_params
from main.utils import split_path, HttpResponseReload

from django.utils.log import logger

def Index( request ):
    user = get_user( request )
    logger.info( 'Index page test' )
    if not user:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    FileLibs = MHome.objects.select_related( 'lib' ).filter( user=user )

    libs = []
    for i in FileLibs:
        libs.append( i.lib_id )
    history = MHistory.objects.\
              select_related( 'user', 'lib' ).\
              only( 'lib', 'type', 'message', 'path', 'user__username', 'lib__name' ).\
              filter( lib__in=libs ).\
              order_by( '-id' )[0:8]

    return render( request, "index.html",
                   {
                       'history': history,
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

    history = MHistory.objects.\
              select_related( 'user' ).\
              only( 'lib', 'type', 'message', 'path', 'user__username' ).\
              filter( lib=home_id ).\
              order_by( '-id' )[0:5]

    patharr = split_path( path )

    Storage = FileStorage( FileLib.lib.path )
    files = Storage.listdir( path )

    return render( request, "browser.html",
                   {
                       'path': path,
                       'patharr': patharr,
                       'history': history,
                       'home_id': home_id,
                       'home': FileLib.lib.name,
                       'permission': FileLib.permission,
                       'files': files,
                       } )


def Action( request, command ):
    home = request.GET['h']
    path = request.GET['p']

    user = get_user( request )
    FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=home )
    Storage = FileStorage( FileLib.lib.path )

    history = MHistory( user=user, lib=FileLib.lib )
    history.path = Storage.path.dirname( path )
    if command == 'add':
        try:
            if not FileLib.permission.edit:
                raise PermissionError( u'You have no permission to create new directory' )
            name = request.GET['n']
            dir = Storage.path.join( path, name )
            Storage.mkdir( dir )
            messages.success( request, "directory '%s' successfully created" % name )

            history.type = MHistory.ADD
            history.message = "dir '%s' created" % name
            history.path = dir
            history.save( )
        except StorageError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    elif command == 'delete':
        try:
            if not FileLib.permission.delete:
                raise PermissionError( u'You have no permission to delete' )
            Storage.totrash( path )
            messages.success( request, "'%s' successfully moved to trash" % Storage.path.name( path ) )

            history.type = MHistory.DELETE
            history.message = "'%s' moved to trash" % Storage.path.name( path )
            history.save( )
        except StorageError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    elif command == 'rename':
        try:
            if not FileLib.permission.edit:
                raise PermissionError( u'You have no permission to rename' )
            name = request.GET['n']
            Storage.rename( path, name )
            messages.success( request, "'%s' successfully rename to '%s'" % (Storage.path.name( path ), name) )

            history.type = MHistory.CHANGE
            history.message = "'%s' renamed" % name
            history.save( )
        except StorageError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    elif command == 'move':
        try:
            if not FileLib.permission.move:
                raise PermissionError( u'You have no permission to move' )
            path2 = request.GET['p2']
            path2 = Storage.path.norm( Storage.path.dirname( path ), path2 )
            Storage.move( path, path2 )
            messages.success( request, "'%s' successfully moved to '%s'" % (Storage.path.name( path ), path2) )

            history.type = MHistory.CHANGE
            history.message = "'%s' moved" % Storage.path.name( path )
            history.path = path2
            history.save( )
        except StorageError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    #return render( request, "browser.html", {})
    return HttpResponseReload( request )


@csrf_exempt
def Upload( request ):
    if request.method == 'POST':
        try:
            user = get_user( request )

            lib_id = request.POST['h']
            path = request.POST['p']

            FileLib = MHome.objects.select_related( 'lib' ).get( user=user, lib__id=lib_id )
            if not FileLib.permission.upload:
                raise PermissionError( u'You have no permission to upload' )
            
            Storage = FileStorage( FileLib.lib.path )

            files = request.FILES.getlist( 'files' )
            if len( files ) > 3:
                history = MHistory( user=user, lib=FileLib.lib, type=MHistory.ADD, path=path )
                history.message = "Uploaded %s files" % len( files )
                for file in files:
                    fool_path = Storage.path.join( path, file.name )
                    Storage.save( fool_path, file )
                history.save( )
            else:
                for file in files:
                    fool_path = Storage.path.join( path, file.name )
                    Storage.save( fool_path, file )
                    history = MHistory( user=user, lib=FileLib.lib, type=MHistory.ADD, path=path )
                    history.message = "Uploaded '%s'" % file.name
                    history.save( )
        except PermissionError as e:
            messages.error( request, e )

    return HttpResponseReload( request )


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
