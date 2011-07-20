# -*- coding: utf-8 -*-
# Create your views here.
from datetime import datetime
import hashlib
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt

from limited.storage import FileStorage, FileError, FileNotExist
from limited.models import MHome, MHistory, PermissionError, MLink, MFileLib
from limited.controls import Downloads, getFileLib, isUserCanView, getFileLibs
from limited.utils import split_path, HttpResponseReload

logger = logging.getLogger(__name__)

def Index( request ):
    user = request.user
    if not isUserCanView( user ):
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    FileLibs = getFileLibs( user )

    # get ids for SELECT HAVE statement
    libs = []
    for i in FileLibs:
        libs.append( i.lib_id )
    # SELECT Histories messages
    # from all available libs    
    history = MHistory.objects.\
              select_related( 'user', 'lib' ).\
              only( 'lib', 'type', 'name', 'path', 'extra', 'user__username', 'lib__name' ).\
              filter( lib__in=libs ).\
              order_by( '-time' )[0:8]

    AnonFileLibs = []
    if not user.is_anonymous( ) and not user.is_superuser:
        AnonFileLibs = MHome.objects.select_related( 'lib' )\
            .filter( user=settings.LIMITED_ANONYMOUS_ID )\
            .exclude( lib__in=libs )

    return render( request, "limited/index.html", {
        'history': history,
        'FileLibs': FileLibs,
        'AnonFileLibs': AnonFileLibs,
        } )


@csrf_exempt
def Browser( request, id ):
    if not isUserCanView( request.user ):
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    home_id = int( id )
    path = request.GET.get('p', '')

    try:
        FileLib = getFileLib( request.user, home_id)

        history = MHistory.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'user__username' ).\
                  filter( lib=home_id ).\
                  order_by( '-id' )[0:5]

        patharr = split_path( path )

        File = FileStorage( FileLib.lib.path )
        files = File.listdir( path )

    except MHome.DoesNotExist:
        logger.error( "Browser. No such file lib or you don't have permissions. home_id:{0}, path:{1}".format( home_id, path ) )
        return RenderError( request, "No such file lib or you don't have permissions" )
    except FileError as e:
        logger.error( "Browser. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
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


def History( request, id ):

    if not isUserCanView( request.user ):
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    home_id = int( id )

    try:
        FileLib = getFileLib( request.user, home_id)

        history = MHistory.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'time', 'user__username' ).\
                  filter( lib=home_id ).\
                  order_by( '-id' )[0:30]

        patharr = split_path( 'History' )

    except MHome.DoesNotExist:
        logger.error( "History. No such file lib or you don't have permissions. home_id:{0}".format( home_id ) )
        return RenderError( request, "No such file lib or you don't have permissions" )

    return render( request, "limited/history.html", {
        'patharr': patharr,
        'history': history,
        'home_id': home_id,
        'home': FileLib.lib.name,
        'permission': FileLib.permission,
        } )


def Trash( request, id ):
    if not isUserCanView( request.user ):
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    home_id = int( id )

    try:
        FileLib = getFileLib( request.user, home_id)

        history = MHistory.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'user__username' ).\
                  filter( lib=home_id ).\
                  order_by( '-id' )[0:5]

        patharr = split_path( 'Trash' )

        File = FileStorage( FileLib.lib.path )
        if not File.exists( ".TrashBin" ):
            File.mkdir( ".TrashBin" )
        files = File.listdir( '.TrashBin' )

    except MHome.DoesNotExist:
        logger.error( "Trash. No such file lib or you don't have permissions. home_id:{0}".format( home_id ) )
        raise Http404( "No such file lib or you don't have permissions" )
    except FileNotExist as e:
        return RenderError( request, "No any trash files" )
    except FileError as e:
        logger.error( "Trash. {0}. home_id:{1}".format( e, home_id ) )
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
def Action( request, id, command ):
    home_id = int( id )
    path = request.GET.get('p', '')
    
    FileLib = getFileLib( request.user, home_id)
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
                #history.type = MHistory.CREATE
                #history.path = dir
                #history.save( )

        except FileError as e:
            logger.error( "Action add. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( "Action add. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )

    # Delete from FS
    elif command == 'delete':
        try:
            if not FileLib.permission.delete:
                raise PermissionError( u'You have no permission to delete' )
            Storage.delete( path )
            messages.success( request, "'%s' successfully deleted" % Storage.path.name( path ) )
            history.user = FileLib.user
            history.type = MHistory.DELETE
            history.name = Storage.path.name( path )
            history.save( )
        except FileError as e:
            logger.error( "Action delete. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( "Action delete. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )

    # Move to special directory
    elif command == 'trash':
        try:
            if not FileLib.permission.delete:
                raise PermissionError( u'You have no permission to delete' )
            Storage.totrash( path )
            messages.success( request, "'%s' successfully moved to trash" % Storage.path.name( path ) )
            history.user = FileLib.user
            history.type = MHistory.TRASH
            history.name = Storage.path.name( path )
            history.save( )
        except FileError as e:
            logger.error( "Action trash. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( "Action trash. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )

    # GET 'n' - new file name
    elif command == 'rename':
        try:
            if not FileLib.permission.edit:
                raise PermissionError( u'You have no permission to rename' )
            name = request.GET['n']
            Storage.rename( path, name )
            messages.success( request, "'%s' successfully rename to '%s'" % (Storage.path.name( path ), name) )
            history.user = FileLib.user
            history.type = MHistory.RENAME
            history.name = name
            history.save( )
        except FileError as e:
            logger.error( "Action rename. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( "Action rename. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
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
            history.user = FileLib.user
            history.type = MHistory.MOVE
            history.name = Storage.path.name( path )
            history.path = path2
            history.save( )
        except FileError as e:
            logger.error( "Action move. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( "Action move. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
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
                history.user = FileLib.user
                history.type = MHistory.LINK
                history.name = Storage.path.name( path )
                history.extra = hash
                history.path = Storage.path.dirname( path )
                history.save( )
            else:
                logger.error( "Action link. You have no permission to create links. home_id:{0}, path:{0}".format( home_id, path ) )
                raise PermissionError( u'You have no permission to create links' )

        except PermissionError as e:
            logger.error( "Action link. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
            messages.error( request, e )

    elif command == 'zip':
        try:
            if path.endswith( '.zip' ):
                Storage.unzip( path )
            else:
                Storage.zip( path )
        except PermissionError as e:
            logger.error( "Action zip. {0}. home_id:{1}, path:{2}".format( e, home_id, path ) )
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
def Upload( request, id ):
    if request.method == 'POST':
        try:
            lib_id = int(id)
            path = request.POST['p']

            FileLib = getFileLib( request.user, lib_id)
            if not FileLib.permission.upload:
                raise PermissionError( u'You have no permission to upload' )

            Storage = FileStorage( FileLib.lib.path )

            files = request.FILES.getlist( 'files' )
            # if files > 3 just send message 'Uploaded N files'
            if len( files ) > 3:
                history = MHistory( user=FileLib.user, lib=FileLib.lib, type=MHistory.UPLOAD, path=path )
                history.name = "%s files" % len( files )
                for file in files:
                    fool_path = Storage.path.join( path, file.name )
                    Storage.save( fool_path, file )
                history.save( )
            # else create message for each file
            else:
                for file in files:
                    fool_path = Storage.path.join( path, file.name )
                    Storage.save( fool_path, file )
                    history = MHistory( user=FileLib.user, lib=FileLib.lib, type=MHistory.UPLOAD, path=path )
                    history.name = file.name
                    history.save( )
        except PermissionError as e:
            dfiles = ["{0}:{1}".format(x.name,x.size) for x in files]
            logger.error( "Upload. {0}. home_id:{1}, path:{2}, files:{3}".format( e, lib_id, path, dfiles ) )
            messages.error( request, e )

    return HttpResponseReload( request )


# Download files, folders whit checked permissions
# GET 'h' - home id, 'p' - path
def Download( request, id ):
    if request.method == 'GET':
        if not isUserCanView( request.user ):
            return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

        home_id = int( id )
        path = request.GET.get('p', '')

        FileLib = getFileLib( request.user, home_id)

        response = Downloads( FileLib.lib.path, path )

        if not response:
            logger.error( "Download. No file or directory find. home_id:{0}, path:{1}".format( home_id, path ) )
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
        logger.info("No link found by hash %s" % hash)
        raise Http404( 'We are sorry. But such object does not exists or link is out of time' )
    link = link[0]

    Lib = MFileLib.objects.select_related( 'lib' ).get( id=link.lib_id )
    response = Downloads( Lib.path, link.path )
    if not response:
        logger.error( "Link. No file or directory find. hash:{0}".format( hash ) )
        return RenderError( request, 'No file or directory find' )

    return response


def RenderError( request, message ):
    return render( request, "limited/error.html", {
        'message': message,
        } )