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
from limited.models import Home, History, Link, FileLib
from limited.models import PermissionError
from limited.controls import file_response, get_home, is_login_need, get_homes, get_user
from limited.utils import split_path, HttpResponseReload

logger = logging.getLogger(__name__)

def IndexView( request ):
    """
    Index page with list of available libs for user and history widget

    template :template:`limited/index.html`
    """
    user = request.user
    if not is_login_need( user ):
        return HttpResponseRedirect( u"%s?next=%s" % (settings.LOGIN_URL, request.path) )

    Homes = get_homes( user )

    # get ids for SELECT HAVE statement
    libs = []
    for i in Homes:
        libs.append( i.lib_id )

    AnonHomes = []
    if not user.is_anonymous( ) and not user.is_superuser:
        AnonHomes = Home.objects.select_related( 'lib' )\
            .filter( user=settings.LIMITED_ANONYMOUS_ID )\
            .exclude( lib__in=libs )

    # append Anon user libs for history
    for i in AnonHomes:
        if i.lib_id not in libs:
            libs.append( i.lib_id )

    # SELECT Histories messages
    # from all available libs    
    history = History.objects.\
              select_related( 'user', 'lib' ).\
              only( 'lib', 'type', 'name', 'path', 'extra', 'user__username', 'lib__name' ).\
              filter( lib__in=libs ).\
              order_by( '-time' )[0:8]

    return render( request, "limited/index.html", {
        'history': history,
        'Homes': Homes,
        'AnonHomes': AnonHomes,
        } )


@csrf_exempt
def FilesView( request, id ):
    """
    Main browser and history widget

    template :template:`limited/browser.html`
    """
    if not is_login_need( request.user ):
        return HttpResponseRedirect( u"%s?next=%s" % (settings.LOGIN_URL, request.path) )

    lib_id = int( id )
    path = request.GET.get('p', '')

    try:
        home = get_home( request.user, lib_id )

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:5]

        patharr = split_path( path )

        File = FileStorage( home.lib.get_path() )
        files = File.listdir( path )

    except Home.DoesNotExist:
        logger.error( u"Browser. No such file lib or you don't have permissions. home_id:{0}, path:{1}".format( lib_id, path ) )
        return RenderError( request, u"No such file lib or you don't have permissions" )
    except FileError as e:
        logger.error( u"Browser. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
        return RenderError( request, e )

    return render( request, u"limited/files.html", {
        'path': path,
        'patharr': patharr,
        'history': history,
        'home_id': lib_id,
        'home': home.lib.name,
        'permission': home.permission,
        'files': files,
        } )


def HistoryView( request, id ):
    """
    Fool history browser

    template :template:`limited/history.html`
    """
    if not is_login_need( request.user ):
        return HttpResponseRedirect( u"%s?next=%s" % (settings.LOGIN_URL, request.path) )

    lib_id = int( id )

    try:
        Home = get_home( request.user, lib_id)

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'time', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:30]

        patharr = split_path( u"History" )

    except Home.DoesNotExist:
        logger.error( u"History. No such file lib or you don't have permissions. home_id:{0}".format( lib_id ) )
        return RenderError( request, u"No such file lib or you don't have permissions" )

    return render( request, u"limited/history.html", {
        'patharr': patharr,
        'history': history,
        'home_id': lib_id,
        'home': Home.lib.name,
        'permission': Home.permission,
        } )


def TrashView( request, id ):
    """
    Trash folder browser, with only move and delete actions and root directory
    
    template :template:`limited/trash.html`
    """
    if not is_login_need( request.user ):
        return HttpResponseRedirect( u"%s?next=%s" % (settings.LOGIN_URL, request.path) )

    lib_id = int( id )

    try:
        Home = get_home( request.user, lib_id)

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:5]

        patharr = split_path( 'Trash' )

        File = FileStorage( Home.lib.get_path() )
        if not File.exists( u".TrashBin" ):
            File.mkdir( u".TrashBin" )
        files = File.listdir( u".TrashBin" )

    except Home.DoesNotExist:
        logger.error( u"Trash. No such file lib or you don't have permissions. home_id:{0}".format( lib_id ) )
        raise Http404( u"No such file lib or you don't have permissions" )
    except FileNotExist as e:
        return RenderError( request, u"No any trash files" )
    except FileError as e:
        logger.error( u"Trash. {0}. home_id:{1}".format( e, lib_id ) )
        return RenderError( request, e )

    return render( request, u"limited/trash.html", {
        'path': '.TrashBin',
        'patharr': patharr,
        'history': history,
        'home_id': lib_id,
        'home': Home.lib.name,
        'permission': Home.permission,
        'files': files,
        } )


def ActionView( request, id, command ):
    """
    Action add, delete, rename, movem link
    GET 'h' - home id, 'p' - path
    """
    lib_id = int( id )
    path = request.GET.get('p', '')
    
    Home = get_home( request.user, lib_id)
    user = get_user( request.user )
    Storage = FileStorage( Home.lib.get_path() )

    history = History( lib=Home.lib )
    history.path = Storage.path.dirname( path )
    # GET 'n' - folder name
    if command == u"add":
        try:
            if not Home.permission.create:
                raise PermissionError( u"You have no permission to create new directory" )
            name = request.GET['n']
            # If it link - download it
            # No any messages on success
            if name.startswith( u"http://" ):
                Storage.download( path, name )
                messages.success( request, u"file '%s' added for upload" % name )
            # Just create new directory
            else:
                dir = Storage.path.join( path, name )
                Storage.mkdir( dir )
                messages.success( request, u"directory '%s' successfully created" % name )
                #history.message = "dir '%s' created" % name
                #history.type = History.CREATE
                #history.path = dir
                #history.save( )

        except FileError as e:
            logger.error( u"Action add. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( u"Action add. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # Delete from FS
    elif command == u"delete":
        try:
            if not Home.permission.delete:
                raise PermissionError( u'You have no permission to delete' )
            Storage.delete( path )
            messages.success( request, u"'%s' successfully deleted" % Storage.path.name( path ) )
            history.user = user
            history.type = History.DELETE
            history.name = Storage.path.name( path )
            history.save( )
        except FileError as e:
            logger.error( u"Action delete. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( u"Action delete. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # Move to special directory
    elif command == u"trash":
        try:
            if not Home.permission.delete:
                raise PermissionError( u"You have no permission to delete" )
            Storage.totrash( path )
            messages.success( request, u"'%s' successfully moved to trash" % Storage.path.name( path ) )
            history.user = user
            history.type = History.TRASH
            history.name = Storage.path.name( path )
            history.save( )
        except FileError as e:
            logger.error( u"Action trash. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( u"Action trash. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # GET 'n' - new file name
    elif command == u"rename":
        try:
            if not Home.permission.edit:
                raise PermissionError( u"You have no permission to rename" )
            name = request.GET['n']
            Storage.rename( path, name )
            messages.success( request, u"'%s' successfully rename to '%s'" % (Storage.path.name( path ), name) )
            history.user = user
            history.type = History.RENAME
            history.name = name
            history.save( )
        except FileError as e:
            logger.error( u"Action rename. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( u"Action rename. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # GET 'p2' - new directory path
    elif command == u"move":
        try:
            if not Home.permission.move:
                raise PermissionError( u"You have no permission to move" )
            path2 = request.GET['p2']
            path2 = Storage.path.norm( Storage.path.dirname( path ), path2 )
            Storage.move( path, path2 )
            messages.success( request, u"'%s' successfully moved to '%s'" % (Storage.path.name( path ), path2) )
            history.user = user
            history.type = History.MOVE
            history.name = Storage.path.name( path )
            history.path = path2
            history.save( )
        except FileError as e:
            logger.error( "Action move. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )
        except PermissionError as e:
            logger.error( u"Action move. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    elif command == u"link":
        try:
            # Get MaxAge
            #age = request.GET['a']
            hash = hashlib.md5( smart_str( path ) ).hexdigest( )[0:12]
            domain = Site.objects.get_current( ).domain

            # TODO: if links exists where hash and `time`+ `maxage` > NOW()
            # +! work only with MySQL
            # extra( where=[' DATE_ADD(`time` , INTERVAL `maxage` SECOND) > %s'], params=[datetime.now( )] ).\
            link = Link.objects.filter( hash=hash )\
            .order_by( '-time' )\
            .exists( )
            # if exist and not expired
            if link:
                messages.success( request, u"link already exists '<a href=\"http://{0}/link/{1}\">http://{0}/link/{1}<a>'".format(domain, hash) )
            # else create new one
            elif Home.permission.create:
                Link( hash=hash, lib=Home.lib, path=path ).save( )
                messages.success( request, u"link successfully created to '<a href=\"http://{0}/link/{1}\">http://{0}/link/{1}<a>'".format(domain, hash) )
                history.user = user
                history.type = History.LINK
                history.name = Storage.path.name( path )
                history.extra = hash
                history.path = Storage.path.dirname( path )
                history.save( )
            else:
                logger.error( u"Action link. You have no permission to create links. home_id:{0}, path:{0}".format( lib_id, path ) )
                raise PermissionError( u"You have no permission to create links" )

        except PermissionError as e:
            logger.errorlogger.error( u"Action link. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    elif command == u"zip":
        try:
            if not Home.permission.edit:
                raise PermissionError( u"You have no permission to zip" )

            if path.endswith( u".zip" ):
                Storage.unzip( path )
            else:
                Storage.zip( path )
        except PermissionError as e:
            logger.error( u"Action zip. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    elif command == u"size":
        size = Storage.size( path, dir=True, cached=True )
        size = filesizeformat( size )
        return HttpResponse( size )

    #return render( request, "browser.html", {})
    return HttpResponseReload( request )


@csrf_exempt
def UploadView( request, id ):
    """
    Files upload to
    POST 'h' - home id, 'p' - path, 'files'
    """
    if request.method == u"POST":
        try:
            lib_id = int(id)
            path = request.POST['p']

            home = get_home( request.user, lib_id)
            if not home.permission.upload:
                raise PermissionError( u"You have no permission to upload" )

            user = get_user( request.user )
            storage = FileStorage( home.lib.get_path() )

            files = request.FILES.getlist( u'files' )
            # if files > 3 just send message 'Uploaded N files'
            if len( files ) > 3:
                history = History( user=user, lib=home.lib, type=History.UPLOAD, path=path )
                history.name = u"%s files" % len( files )
                for file in files:
                    fool_path = storage.path.join( path, file.name )
                    storage.save( fool_path, file )
                history.save( )
            # else create message for each file
            else:
                for file in files:
                    fool_path = storage.path.join( path, file.name )
                    storage.save( fool_path, file )
                    history = History( user=user, lib=home.lib, type=History.UPLOAD, path=path )
                    history.name = file.name
                    history.save( )
        except PermissionError as e:
            dfiles = [u"{0}:{1}".format(x.name,x.size) for x in files]
            logger.error( u"Upload. {0}. home_id:{1}, path:{2}, files:{3}".format( e, lib_id, path, dfiles ) )
            messages.error( request, e )

    return HttpResponseReload( request )


def DownloadView( request, id ):
    """
    Download files, folders whit checked permissions
    GET 'h' - home id, 'p' - path
    """
    if request.method == u"GET":
        if not is_login_need( request.user ):
            return HttpResponseRedirect( u"%s?next=%s" % (settings.LOGIN_URL, request.path) )

        lib_id = int( id )
        path = request.GET.get('p', '')

        Home = get_home( request.user, lib_id)

        response = file_response( Home.lib.get_path(), path )

        if not response:
            logger.error( u"Download. No file or directory find. home_id:{0}, path:{1}".format( lib_id, path ) )
            return RenderError( request, u"No file or directory find" )

        return response


def LinkView( request, hash ):
    """
    If link exist Download whitout any permission
    """
    
    # Filter kinks where hash and `time`+ `maxage` > NOW()
    # if len == 0 send error
    # +! work only with MySQL
    link = Link.objects.filter( hash=hash ).\
           extra( where=[ u" DATE_ADD(`time` , INTERVAL `maxage` SECOND) > %s " ], params=[datetime.now( )] ).\
           order_by( '-time' )[0:1]
    if len( link ) == 0:
        logger.info( u"No link found by hash %s" % hash )
        raise Http404( u"We are sorry. But such object does not exists or link is out of time" )
    link = link[0]

    Lib = FileLib.objects.select_related( 'lib' ).get( id=link.lib_id )
    response = file_response( Lib.get_path(), link.path )
    if not response:
        logger.error( u"Link. No file or directory find. hash:{0}".format( hash ) )
        return RenderError( request, u"No file or directory find" )

    return response


def RenderError( request, message ):
    """
    Just link for template :template:`limited/error.html`
    """
    return render( request, u"limited/error.html", {
        'message': message,
        } )