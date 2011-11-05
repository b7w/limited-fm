# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat
from django.views.decorators.csrf import csrf_exempt

from limited import settings
from limited.serve.manager import DownloadManager
from limited.files.storage import FileError, FileNotExist, FilePath
from limited.files.utils import Thread
from limited.models import Home, History, Link
from limited.models import PermissionError
from limited.controls import get_home, get_homes, get_user
from limited.utils import split_path, HttpResponseReload, url_get_filename

logger = logging.getLogger(__name__)

def IndexView( request ):
    """
    Index page with list of available libs for user and history widget

    template :template:`limited/index.html`
    """
    user = request.user
    if user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    Homes = get_homes( user )

    # get ids for SELECT HAVE statement
    libs = []
    for i in Homes:
        libs.append( i.lib_id )

    AnonHomes = []
    if not user.is_anonymous( ) and not user.is_superuser:
        AnonHomes = Home.objects.select_related( 'lib' )\
            .filter( user=settings.LIMITED_ANONYMOUS_ID )\
            .exclude( lib__in=libs )\
            .order_by( 'lib__name' )

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
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )
    
    lib_id = int( id )
    path = request.GET.get('p', '')

    try:
        home = get_home( request.user, lib_id )

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:8]

        patharr = split_path( path )

        File = home.lib.getStorage()
        files = File.listdir( path )

        allowed = {}
        allowed['only'] = '|'.join( settings.LIMITED_FILES_ALLOWED["ONLY"] )
        allowed['except'] = '|'.join( settings.LIMITED_FILES_ALLOWED["EXCEPT"] )

    except ObjectDoesNotExist:
        logger.error( u"Files. No such file lib or you don't have permissions. home_id:{0}, path:{1}".format( lib_id, path ) )
        return RenderError( request, u"No such file lib or you don't have permissions" )
    except FileError as e:
        logger.error( u"Files. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
        return RenderError( request, e )

    return render( request, u"limited/files.html", {
        'pathname': request.path,
        'path': path,
        'patharr': patharr,
        'history': history,
        'home_id': lib_id,
        'home': home.lib.name,
        'permission': home.permission,
        'files': files,
        'allowed': allowed,
        } )


def HistoryView( request, id ):
    """
    Fool history browser

    template :template:`limited/history.html`
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )
    
    lib_id = int( id )

    try:
        home = get_home( request.user, lib_id)

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'time', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:30]

        patharr = split_path( u"History" )

    except ObjectDoesNotExist:
        logger.error( u"History. No such file lib or you don't have permissions. home_id:{0}".format( lib_id ) )
        return RenderError( request, u"No such file lib or you don't have permissions" )

    return render( request, u"limited/history.html", {
        'pathname': request.path,
        'patharr': patharr,
        'history': list(history),
        'home_id': lib_id,
        'home': home.lib.name,
        'permission': home.permission,
        } )


def TrashView( request, id ):
    """
    Trash folder browser, with only move and delete actions and root directory
    
    template :template:`limited/trash.html`
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )
    
    lib_id = int( id )

    try:
        home = get_home( request.user, lib_id)

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'name', 'path', 'extra', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:5]

        patharr = split_path( 'Trash' )

        File = home.lib.getStorage()
        if not File.exists( settings.LIMITED_TRASH_PATH ):
            File.mkdir( settings.LIMITED_TRASH_PATH )
        files = File.listdir( settings.LIMITED_TRASH_PATH )

    except ObjectDoesNotExist:
        logger.error( u"Trash. No such file lib or you don't have permissions. home_id:{0}".format( lib_id ) )
        return RenderError( request, u"No such file lib or you don't have permissions" )
    except FileError as e:
        logger.error( u"Trash. {0}. home_id:{1}".format( e, lib_id ) )
        return RenderError( request, e )

    return render( request, u"limited/trash.html", {
        'pathname': request.path,
        'path': settings.LIMITED_TRASH_PATH,
        'patharr': patharr,
        'history': history,
        'home_id': lib_id,
        'home': home.lib.name,
        'permission': home.permission,
        'files': files,
        } )


def ActionView( request, id, command ):
    """
    Action add, delete, rename, movem link
    GET 'h' - home id, 'p' - path
    than redirect back
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )
    
    lib_id = int( id )
    path = request.GET.get('p', '')
    
    home = get_home( request.user, lib_id)
    user = get_user( request.user )
    Storage = home.lib.getStorage()

    history = History( lib=home.lib )
    history.path = FilePath.dirname( path )
    # GET 'n' - folder name
    if command == u"add":
        try:
            if not home.permission.create:
                raise PermissionError( u"You have no permission to create new directory" )
            name = request.GET['n']
            # If it link - download it
            # No any messages on success
            if name.startswith( u"http://" ):
                filename = url_get_filename( name )
                path = FilePath.join( path, filename )
                #TODO: Fucking TransactionManagementError don't now how to fix
                # In a Thread we set signal=False to not update DB
                T = Thread()
                T.setView( Storage.download, name, path, signal=False )
                T.start()
                messages.success( request, u"file '%s' added for upload" % filename )
            # Just create new directory
            else:
                dir = FilePath.join( path, name )
                Storage.mkdir( dir )
                messages.success( request, u"directory '%s' successfully created" % name )
                #history.message = "dir '%s' created" % name
                #history.type = History.CREATE
                #history.path = dir
                #history.save( )

        except ( PermissionError, FileError ) as e:
            logger.error( u"Action add. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # Delete from FS
    elif command == u"delete":
        try:
            if not home.permission.delete:
                raise PermissionError( u'You have no permission to delete' )
            Storage.remove( path )
            messages.success( request, u"'%s' successfully deleted" % FilePath.name( path ) )
            history.user = user
            history.type = History.DELETE
            history.name = FilePath.name( path )
            history.save( )
        except ( PermissionError, FileError ) as e:
            logger.error( u"Action delete. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # Move to special directory
    elif command == u"trash":
        try:
            if not home.permission.delete:
                raise PermissionError( u"You have no permission to delete" )
            Storage.totrash( path )
            messages.success( request, u"'%s' successfully moved to trash" % FilePath.name( path ) )
            history.user = user
            history.type = History.TRASH
            history.name = FilePath.name( path )
            history.save( )
        except ( PermissionError, FileError ) as e:
            logger.error( u"Action trash. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # GET 'n' - new file name
    elif command == u"rename":
        try:
            if not home.permission.edit:
                raise PermissionError( u"You have no permission to rename" )
            name = request.GET['n']
            Storage.rename( path, name )
            messages.success( request, u"'%s' successfully rename to '%s'" % ( FilePath.name( path ), name) )
            history.user = user
            history.type = History.RENAME
            history.name = name
            history.save( )
        except ( PermissionError, FileError ) as e:
            logger.error( u"Action rename. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # GET 'p2' - new directory path
    elif command == u"move":
        try:
            if not home.permission.move:
                raise PermissionError( u"You have no permission to move" )
            path2 = request.GET['p2']
            if path2[0] == u'/':
                path2 = path2[1:]
                Storage.move( path, path2 )
            elif path2[0] == u'.':
                tmp = FilePath.join( FilePath.dirname( path ), path2 )
                path2 = FilePath.norm( tmp )
                Storage.move( path, path2 )
            else:
                path2 = FilePath.join( FilePath.dirname( path ), path2 )
                Storage.move( path, path2 )
            #path2 = FilePath.norm( FilePath.dirname( path ), path2 )
            #Storage.move( path, path2 )
            messages.success( request, u"'%s' successfully moved to '%s'" % ( FilePath.name( path ), path2) )
            history.user = user
            history.type = History.MOVE
            history.name = FilePath.name( path )
            history.path = path2
            history.save( )
        except ( PermissionError, FileError ) as e:
            logger.error( u"Action move. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    elif command == u"link":
        try:
            domain = Site.objects.get_current( ).domain
            link = Link.objects.find( Link.get_hash( home.lib_id, path ) )
            # if exist and not expired
            if link:
                messages.success( request, u"link already exists <a href=\"http://{0}/link/{1}\">http://{0}/link/{1}<a>".format(domain, link.hash) )
            # else create new one
            elif home.permission.create:
                #Link( hash=hash, lib=home.lib, path=path ).save( )
                link = Link.objects.add( home.lib, path )

                messages.success( request, u"link successfully created to '<a href=\"http://{0}/link/{1}\">http://{0}/link/{1}<a>'".format(domain, link.hash) )
                history.user = user
                history.type = History.LINK
                history.name = FilePath.name( path )
                history.extra = link.hash
                history.path = FilePath.dirname( path )
                history.save( )
            else:
                logger.error( u"Action link. You have no permission to create links. home_id:{0}, path:{0}".format( lib_id, path ) )
                raise PermissionError( u"You have no permission to create links" )

        except ( PermissionError, FileError ) as e:
            logger.info( u"Action link. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    elif command == u"zip":
        try:
            if not home.permission.edit:
                raise PermissionError( u"You have no permission to zip" )

            if path.endswith( u".zip" ):
                Storage.unzip( path )
            else:
                Storage.zip( path )
        except ( PermissionError, FileError ) as e:
            logger.info( u"Action zip. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    elif command == u"size":
        size = Storage.size( path, dir=True, cached=True )
        size = filesizeformat( size )
        return HttpResponse( size )

    return HttpResponseReload( request )


def ActionClear( request, id, command ):
    """
    Clear trash or cache folders
    and than redirect back
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )
    
    lib_id = int( id )

    home = get_home( request.user, lib_id)
    Storage = home.lib.getStorage()

    if command == u"trash":
        try:
            if not request.user.is_staff:
                raise PermissionError( u"You have no permission to clear trash" )
            Storage.clear( settings.LIMITED_TRASH_PATH )
        except ( PermissionError, FileError ) as e:
            logger.info( u"Action clear trash. {0}. home_id:{1}".format( e, lib_id ) )
            messages.error( request, e )

    elif command == u"cache":
        try:
            if not request.user.is_staff:
                raise PermissionError( u"You have no permission to clear cache" )
            Storage.clear( settings.LIMITED_CACHE_PATH )
        except ( PermissionError, FileError ) as e:
            logger.info( u"Action clear trash. {0}. home_id:{1}".format( e, lib_id ) )
            messages.error( request, e )

    return HttpResponseReload( request )


@csrf_exempt
def UploadView( request, id ):
    """
    Files upload to
    POST 'h' - home id, 'p' - path, 'files'
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )
    
    if request.method == u"POST":
        try:
            lib_id = int(id)
            path = request.POST['p']

            home = get_home( request.user, lib_id)
            if not home.permission.upload:
                raise PermissionError( u"You have no permission to upload" )

            user = get_user( request.user )
            storage = home.lib.getStorage()

            files = request.FILES.getlist( u'files' )

            for file in files:
                pair = file.name.rsplit( '.' )
                if pair.__len__() > 1:
                    name, ext = pair
                    if settings.LIMITED_FILES_ALLOWED['ONLY'] != []:
                        if ext.lower() not in settings.LIMITED_FILES_ALLOWED['ONLY']:
                            raise PermissionError( u"This type of file '{0}' is not allowed for upload!".format( file.name ) )
                    elif ext.lower() in settings.LIMITED_FILES_ALLOWED['EXCEPT']:
                        raise PermissionError( u"This type of file '{0}' is not allowed for upload!".format( file.name ) )
                    
            history = History( user=user, lib=home.lib, type=History.UPLOAD, path=path )
            history.name = []
            # file paths to delete them after any Exception
            file_paths = []
            for file in files:
                fool_path = FilePath.join( path, file.name )
                name = storage.save( fool_path, file )
                file_paths.append( name )
            history.name = [ FilePath.name( i ) for i in file_paths ]
            history.save( )

        except ObjectDoesNotExist:
            logger.error( u"Upload. No such file lib or you don't have permissions. home_id:{0}".format( lib_id ) )
            return RenderError( request, u"No such file lib or you don't have permissions" )
        except PermissionError as e:
            logger.info( u"Upload. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )
        except Exception:
            for file in file_paths:
                if storage.exists( file ):
                    storage.remove( file )
            raise 

    return HttpResponseReload( request )


def DownloadView( request, id ):
    """
    Download files, folders whit checked permissions
    GET 'h' - home id, 'p' - path
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )
    
    if request.method == u"GET":
        lib_id = int( id )
        path = request.GET.get( 'p', '' )

        try:
            home = get_home( request.user, lib_id )
            manager = DownloadManager( home.lib )
            if manager.is_need_processing( path ):
                manager.process( path )
                messages.info( request, u"File to big and need time to process. Try again a little bit later" )
                return HttpResponseReload( request )
            else:
                response = manager.build( path )

        except ObjectDoesNotExist:
            logger.error( u"Download. No such file lib or you don't have permissions. home_id:{0}".format( lib_id ) )
            return RenderError( request, u"No such file lib or you don't have permissions" )
        except FileNotExist as e:
            logger.error( u"Download. No file or directory find. home_id:{0}, path:{1}".format( lib_id, path ) )
            return RenderError( request, u"No file or directory find" )

        return response


def LinkView( request, hash ):
    """
    If link exist Download without any permission
    """
    try:
        link = Link.objects.find( hash )
        if not link:
            logger.info( u"No link found by hash %s" % hash )
            return RenderError( request, u"We are sorry. But such object does not exists or link is out of time" )

        manager = DownloadManager( link.lib )
        if manager.is_need_processing( link.path ):
            manager.process( link.path )
            messages.info( request, u"File to big and need time to process. Try again a little bit later" )
            return HttpResponseReload( request )
        else:
            response = manager.build( link.path )

    except FileNotExist as e:
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
