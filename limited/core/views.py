# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat

from limited.core import settings
from limited.core.serve.manager import DownloadManager
from limited.core.files.storage import FileError, FileNotExist
from limited.core.files.utils import Thread, FilePath
from limited.core.models import Home, History, Link, Profile
from limited.core.models import PermissionError
from limited.core.controls import get_home, get_homes, get_user
from limited.core.utils import split_path, HttpResponseReload, url_get_filename, check_file_name, MailFileNotify, urlbilder

logger = logging.getLogger( __name__ )

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
              only( 'lib', 'type', 'files', 'path', 'extra', 'user__username', 'lib__name' ).\
              filter( lib__in=libs ).\
              order_by( '-time' )[0:8]

    rss_token = None if user.is_anonymous() else Profile.objects.get(user=user).rss_token

    return render( request, "limited/index.html", {
        'history': history,
        'Homes': Homes,
        'AnonHomes': AnonHomes,
        'rss_token': rss_token,
        } )


def FilesView( request, id ):
    """
    Main browser and history widget

    template :template:`limited/browser.html`
    """
    user = request.user
    if user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    lib_id = int( id )
    path = request.GET.get( 'p', '' )
    if not FilePath.check(path, norm=True):
        logger.error( u"Files. Path check fail. home_id:{0}, path:{1}".format( lib_id, path ) )
        return RenderError( request, u"IOError, Permission denied" )

    try:
        home = get_home( user, lib_id )

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'files', 'path', 'extra', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:8]

        patharr = split_path( path )

        File = home.lib.getStorage( )
        files = File.listdir( path )

        # Check if iViewer is enable and there is at least 2 jpg
        lViewer = False
        if settings.LIMITED_LVIEWER:
            images = 0
            for file in files:
                tmp = file["name"].lower( )
                if tmp.endswith( ".jpg" ) or tmp.endswith( ".jpeg" ):
                    images += 1
            lViewer = images > 1

        allowed = {}
        allowed['only'] = '|'.join( settings.LIMITED_FILES_ALLOWED["ONLY"] ).replace( '\\', '\\\\' )
        allowed['except'] = '|'.join( settings.LIMITED_FILES_ALLOWED["EXCEPT"] ).replace( '\\', '\\\\' )
        allowed['message'] = settings.LIMITED_FILES_MESSAGE

        rss_token = None if user.is_anonymous() else Profile.objects.get(user=user).rss_token

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
        'rss_token': rss_token,
        'lviewer': lViewer,
        } )


def HistoryView( request, id ):
    """
    Fool history browser

    template :template:`limited/history.html`
    """
    user = request.user
    if user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    lib_id = int( id )

    try:
        home = get_home( user, lib_id )

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'files', 'path', 'extra', 'time', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:30]

        patharr = split_path( u"History" )

        rss_token = None if user.is_anonymous() else Profile.objects.get(user=user).rss_token

    except ObjectDoesNotExist:
        logger.error( u"History. No such file lib or you don't have permissions. home_id:{0}".format( lib_id ) )
        return RenderError( request, u"No such file lib or you don't have permissions" )

    return render( request, u"limited/history.html", {
        'pathname': request.path,
        'patharr': patharr,
        'history': list( history ),
        'home_id': lib_id,
        'home': home.lib.name,
        'permission': home.permission,
        'rss_token': rss_token,
        } )


def TrashView( request, id ):
    """
    Trash folder browser, with only move and delete actions and root directory
    
    template :template:`limited/trash.html`
    """
    user = request.user
    if user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    lib_id = int( id )

    try:
        home = get_home(user, lib_id )

        history = History.objects.\
                  select_related( 'user' ).\
                  only( 'lib', 'type', 'files', 'path', 'extra', 'user__username' ).\
                  filter( lib=lib_id ).\
                  order_by( '-id' )[0:5]

        patharr = split_path( 'Trash' )

        File = home.lib.getStorage( )
        files = File.trash.listdir( )

        rss_token = None if user.is_anonymous() else Profile.objects.get(user=user).rss_token

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
        'rss_token': rss_token,
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
    path = request.GET.get( 'p', '' )
    if not FilePath.check(path, norm=True):
        logger.error( u"Files. Path check fail. home_id:{0}, path:{1}".format( lib_id, path ) )
        return RenderError( request, u"IOError, Permission denied" )

    home = get_home( request.user, lib_id )
    user = get_user( request.user )
    Storage = home.lib.getStorage( )

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
            if name.startswith( u"http://" ) or name.startswith( u"https://" ):
                if not home.permission.http_get:
                    raise PermissionError( u"You have no permission to upload from url" )
                filename = url_get_filename( name )
                path = FilePath.join( path, filename )
                #TODO: Fucking TransactionManagementError don't now how to fix
                # In a Thread we set signal=False to not update DB
                T = Thread( )
                T.setView( Storage.extra.download, name, path, signal=False )
                T.run( ) if settings.TEST else T.start( )
                messages.success( request, u"file '%s' added for upload" % filename )
            # Just create new directory
            else:
                if u'/' in name or u'\\' in name:
                    raise FileError( u"Not supported symbols" )
                if not check_file_name( name ):
                    raise PermissionError( u"This name of directory '{0}' is not allowed for creating!".format( name ) )
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
            history.files = FilePath.name( path )
            history.save( )
        except ( PermissionError, FileError ) as e:
            logger.error( u"Action delete. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
            messages.error( request, e )

    # Move to special directory
    elif command == u"trash":
        try:
            if not home.permission.delete:
                raise PermissionError( u"You have no permission to delete" )
            Storage.trash.totrash( path )
            messages.success( request, u"'%s' successfully moved to trash" % FilePath.name( path ) )
            history.user = user
            history.type = History.TRASH
            history.files = FilePath.name( path )
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
            if not check_file_name( name ):
                raise PermissionError( u"This name '{0}' is invalided!".format( name ) )
            Storage.rename( path, name )
            messages.success( request, u"'%s' successfully rename to '%s'" % ( FilePath.name( path ), name) )
            history.user = user
            history.type = History.RENAME
            history.files = name
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
            messages.success( request, u"'%s' successfully moved to '%s'" % ( FilePath.name( path ), path2) )
            history.user = user
            history.type = History.MOVE
            history.files = FilePath.name( path )
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
                messages.success( request, u"link already exists <a href=\"http://{0}/link/{1}\">http://{0}/link/{1}<a>".format( domain, link.hash ) )
            # else create new one
            elif home.permission.create:
                link = Link.objects.add( home.lib, path )

                messages.success( request, u"link successfully created to '<a href=\"http://{0}/link/{1}\">http://{0}/link/{1}<a>'".format( domain, link.hash ) )
                history.user = user
                history.type = History.LINK
                history.files = FilePath.name( path )
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
                Storage.extra.unzip( path )
            else:
                Storage.extra.zip( path )
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

    home = get_home( request.user, lib_id )
    Storage = home.lib.getStorage( )

    if command == u"trash":
        try:
            if not request.user.is_staff:
                raise PermissionError( u"You have no permission to clear trash" )
            Storage.extra.clear( settings.LIMITED_TRASH_PATH )
        except ( PermissionError, FileError ) as e:
            logger.info( u"Action clear trash. {0}. home_id:{1}".format( e, lib_id ) )
            messages.error( request, e )

    elif command == u"cache":
        try:
            if not request.user.is_staff:
                raise PermissionError( u"You have no permission to clear cache" )
            Storage.extra.clear( settings.LIMITED_CACHE_PATH )
        except ( PermissionError, FileError ) as e:
            logger.info( u"Action clear trash. {0}. home_id:{1}".format( e, lib_id ) )
            messages.error( request, e )

    return HttpResponseReload( request )


def UploadView( request, id ):
    """
    Files upload to
    POST 'h' - home id, 'p' - path, 'files'
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    lib_id = int( id )
    path = request.POST['p']
    if not FilePath.check(path, norm=True):
        logger.error( u"Files. Path check fail. home_id:{0}, path:{1}".format( lib_id, path ) )
        return RenderError( request, u"IOError, Permission denied" )

    if request.method == u"POST":
        file_paths = []
        try:
            # file paths to delete them after any Exception
            home = get_home( request.user, lib_id )
            if not home.permission.upload:
                raise PermissionError( u"You have no permission to upload" )

            user = get_user( request.user )
            storage = home.lib.getStorage( )

            files = request.FILES.getlist( u'files' )

            if not len( files ):
                messages.warning( request, u"No any files selected" )
                return HttpResponseReload( request )

            for file in files:
                if not check_file_name( file.name ):
                    raise PermissionError( settings.LIMITED_FILES_MESSAGE.format( file.name ) )

            history = History( user=user, lib=home.lib, type=History.UPLOAD, path=path )

            for file in files:
                fool_path = FilePath.join( path, file.name )
                name = storage.save( fool_path, file )
                file_paths.append( name )
            history.files = [FilePath.name( i ) for i in file_paths]
            history.save( )

            if settings.LIMITED_EMAIL_NOTIFY['ENABLE']:
                domain = Site.objects.get_current( ).domain
                link = urlbilder( u"browser", lib_id, p=history.path )
                libs = Home.objects.filter( lib_id=lib_id )
                users = [i.user_id for i in libs]

                notify = MailFileNotify( )
                notify.body = u"New files upload to '{0}' by user {1}\n".format(path or '/', history.user)
                notify.body += u"Link http://{0}{1}&hl={2}\n".format(domain, link, history.hash())
                notify.files = [i.name for i in files]
                notify.users = users
                # Hack to stay in one thread and test mail.outbox
                notify.run( ) if settings.TEST else notify.start( )

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
        if not FilePath.check(path, norm=True):
            logger.error( u"Files. Path check fail. home_id:{0}, path:{1}".format( lib_id, path ) )
            return RenderError( request, u"IOError, Permission denied" )

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
