# -*- coding: utf-8 -*-
# Create your views here.
from datetime import datetime
import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt

from limited.storage import FileStorage, FileError
from limited.models import MHome, MHistory, PermissionError, MLink, MFileLib
from limited.controls import get_params, Downloads, getFileLib, isUserCanView, getFileLibs
from limited.utils import split_path, HttpResponseReload

def Index( request ):
    if not isUserCanView( request.user ):
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    FileLibs = getFileLibs( request.user )

    # get ids for SELECT HAVE statement
    libs = []
    for i in FileLibs:
        libs.append( i.lib_id )
    # SELECT Histories messages
    # from all available libs    
    history = MHistory.objects.\
              select_related( 'user', 'lib' ).\
              only( 'lib', 'type', 'message', 'path', 'user__username', 'lib__name' ).\
              filter( lib__in=libs ).\
              order_by( '-time' )[0:8]

    AnonFileLibs = []
    if not request.user.is_anonymous( ):
        tmp = MHome.objects.select_related( 'lib' ).filter( user=settings.LIMITED_ANONYMOUS_ID )
        AnonFileLibs = [ i for i in tmp if i.lib_id not in libs ]

    return render( request, "limited/index.html", {
        'history': history,
        'FileLibs': FileLibs,
        'AnonFileLibs': AnonFileLibs,
        } )


@csrf_exempt
def Browser( request ):
    if not isUserCanView( request.user ):
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    home_id, path = get_params( request )

    try:
        FileLib = getFileLib( request.user, home_id)

        history = MHistory.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'message', 'path', 'user__username' ).\
                  filter( lib=home_id ).\
                  order_by( '-id' )[0:5]

        patharr = split_path( path )

        File = FileStorage( FileLib.lib.path )
        files = File.listdir( path )

    except MHome.DoesNotExist:
        return RenderError( request, "No such file lib or you don't have permissions" )
    except FileError as e:
        return RenderError( request, e )

    return render( request, "limited/browser.html", {
        'path': path,
        'patharr': patharr,
        'history': history,
        'home_id': home_id,
        'home': FileLib.lib.name,
        'permission': FileLib.permission,
        'files': files,
        } )


def Trash( request, id ):
    if not isUserCanView( request.user ):
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    home_id = int( id )

    try:
        FileLib = MHome.objects.select_related( 'lib' ).get( user=request.user, lib__id=home_id )

        history = MHistory.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'message', 'path', 'user__username' ).\
                  filter( lib=home_id ).\
                  order_by( '-id' )[0:5]

        patharr = split_path( 'Trash' )

        File = FileStorage( FileLib.lib.path )
        files = File.listdir( '.TrashBin' )

    except MHome.DoesNotExist:
        raise Http404( "No such file lib or you don't have permissions" )
    except FileError as e:
        return RenderError( request, e )

    return render( request, "limited/trash.html", {
        'path': '.TrashBin',
        'patharr': patharr,
        'history': history,
        'home_id': home_id,
        'home': FileLib.lib.name,
        'permission': FileLib.permission,
        'files': files,
        } )


# Action add, delete, rename, movem link
# GET 'h' - home id, 'p' - path
def Action( request, command ):
    home, path = get_params( request )

    FileLib = getFileLib( request.user, home)
    Storage = FileStorage( FileLib.lib.path )

    history = MHistory( lib=FileLib.lib )
    history.path = Storage.path.dirname( path )
    # GET 'n' - folder name
    if command == 'add':
        try:
            if not FileLib.permission.edit:
                raise PermissionError( u'You have no permission to create new directory' )
            name = request.GET['n']
            # If it link - download it
            # No any messages on success
            if name.startswith( 'http://' ):
                Storage.download( path, name )
                messages.success( request, "file '%s' added for upload" % name )
            # Just create new directory
            else:
                dir = Storage.path.join( path, name )
                Storage.mkdir( dir )
                messages.success( request, "directory '%s' successfully created" % name )
                #history.message = "dir '%s' created" % name
                #history.type = MHistory.ADD
                #history.path = dir
                #history.save( )

        except FileError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    # Delete from FS
    elif command == 'delete':
        try:
            if not FileLib.permission.delete:
                raise PermissionError( u'You have no permission to delete' )
            Storage.delete( path )
            messages.success( request, "'%s' successfully deleted" % Storage.path.name( path ) )
            history.user = request.user
            history.type = MHistory.DELETE
            history.message = "'%s' deleted" % Storage.path.name( path )
            history.save( )
        except FileError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    # Move to special directory
    elif command == 'trash':
        try:
            if not FileLib.permission.delete:
                raise PermissionError( u'You have no permission to delete' )
            Storage.totrash( path )
            messages.success( request, "'%s' successfully moved to trash" % Storage.path.name( path ) )
            history.user = request.user
            history.type = MHistory.DELETE
            history.message = "'%s' moved to trash" % Storage.path.name( path )
            history.save( )
        except FileError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    # GET 'n' - new file name
    elif command == 'rename':
        try:
            if not FileLib.permission.edit:
                raise PermissionError( u'You have no permission to rename' )
            name = request.GET['n']
            Storage.rename( path, name )
            messages.success( request, "'%s' successfully rename to '%s'" % (Storage.path.name( path ), name) )
            history.user = request.user
            history.type = MHistory.CHANGE
            history.message = "'%s' renamed" % name
            history.save( )
        except FileError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    # GET 'p2' - new directory path
    elif command == 'move':
        try:
            if not FileLib.permission.move:
                raise PermissionError( u'You have no permission to move' )
            path2 = request.GET['p2']
            path2 = Storage.path.norm( Storage.path.dirname( path ), path2 )
            Storage.move( path, path2 )
            messages.success( request, "'%s' successfully moved to '%s'" % (Storage.path.name( path ), path2) )
            history.user = request.user
            history.type = MHistory.CHANGE
            history.message = "'%s' moved" % Storage.path.name( path )
            history.path = path2
            history.save( )
        except FileError as e:
            messages.error( request, e )
        except PermissionError as e:
            messages.error( request, e )

    elif command == 'link':
        try:
            # Get MaxAge
            #age = request.GET['a']
            hash = hashlib.md5( smart_str( path ) ).hexdigest( )[0:12]
            domain = Site.objects.get_current( ).domain

            # if links exists where hash and `time`+ `maxage` > NOW()
            # +! work only with MySQL
            link = MLink.objects.filter( hash=hash ).\
            extra( where=[' DATE_ADD(`time` , INTERVAL `maxage` SECOND) > %s'], params=[datetime.now( )] ).\
            order_by( '-time' ).\
            exists( )
            # if exist and not expired
            if link:
                messages.success( request, "link already exists '<a href=\"http://{0}/link/{1}\">http://{0}/link/{1}<a>'".format(domain, hash) )
            # else create new one
            elif not request.user.is_anonymous( ):
                MLink( hash=hash, lib=FileLib.lib, path=path ).save( )
                messages.success( request, "link successfully created to '<a href=\"http://{0}/link/{1}\">http://{0}/link/{1}<a>'".format(domain, hash) )
                history.user = request.user
                history.type = MHistory.ADD
                history.message = "add link for '<a href=\"http://{0}/link/{1}\">{2}<a>'".format(domain, hash, Storage.path.name( path ))
                history.path = Storage.path.dirname( path )
                history.save( )
            else:
                raise PermissionError( u'You have no permission to create links' )

        except PermissionError as e:
            messages.error( request, e )

    elif command == 'zip':
        try:
            if path.endswith( '.zip' ):
                Storage.unzip( path )
            else:
                Storage.zip( path )
        except PermissionError as e:
            messages.error( request, e )

    elif command == 'size':
        size = Storage.size( path, dir=True, cached=True )
        size = filesizeformat( size )
        return HttpResponse( size )

    #return render( request, "browser.html", {})
    return HttpResponseReload( request )


# Files upload to
# POST 'h' - home id, 'p' - path, 'files'
@csrf_exempt
def Upload( request ):
    if request.method == 'POST':
        try:
            lib_id = request.POST['h']
            path = request.POST['p']

            FileLib = getFileLib( request.user, lib_id)
            if not FileLib.permission.upload:
                raise PermissionError( u'You have no permission to upload' )

            Storage = FileStorage( FileLib.lib.path )

            files = request.FILES.getlist( 'files' )
            # if files > 3 just send message 'Uploaded N files'
            if len( files ) > 3:
                history = MHistory( user=request.user, lib=FileLib.lib, type=MHistory.ADD, path=path )
                history.message = "Uploaded %s files" % len( files )
                for file in files:
                    fool_path = Storage.path.join( path, file.name )
                    Storage.save( fool_path, file )
                history.save( )
            # else create message for each file
            else:
                for file in files:
                    fool_path = Storage.path.join( path, file.name )
                    Storage.save( fool_path, file )
                    history = MHistory( user=request.user, lib=FileLib.lib, type=MHistory.ADD, path=path )
                    history.message = "Uploaded '%s'" % file.name
                    history.save( )
        except PermissionError as e:
            messages.error( request, e )

    return HttpResponseReload( request )


# Download files, folders whit checked permissions
# GET 'h' - home id, 'p' - path
def Download( request ):
    if request.method == 'GET':
        if not isUserCanView( request.user ):
            return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

        home, path = get_params( request )

        FileLib = getFileLib( request.user, home)

        response = Downloads( FileLib.lib.path, path )

        if not response:
            return RenderError( request, 'No file or directory find' )

        return response


# If link exist Download whitout any permission
def Link( request, hash ):
    # Filter kinks where hash and `time`+ `maxage` > NOW()
    # if len == 0 send error
    # +! work only with MySQL
    link = MLink.objects.filter( hash=hash ).\
           extra( where=[' DATE_ADD(`time` , INTERVAL `maxage` SECOND) > %s'], params=[datetime.now( )] ).\
           order_by( '-time' )[0:1]
    if len( link ) == 0:
        raise Http404( 'We are sorry. But such object does not exists or link is out of time' )
    link = link[0]

    Lib = MFileLib.objects.select_related( 'lib' ).get( id=link.lib_id )
    response = Downloads( Lib.path, link.path )
    if not response:
        return RenderError( request, 'No file or directory find' )

    return response


def RenderError( request, message ):
    return render( request, "limited/error.html", {
        'message': message,
        } )