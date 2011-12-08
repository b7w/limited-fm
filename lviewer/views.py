# -*- coding: utf-8 -*-

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from lviewer.utils import ResizeImage, ResizeOptions, ResizeOptionsError

from limited import settings
from limited.files.storage import FileError, FileNotExist, FilePath
from limited.files.utils import FileUnicName
from limited.controls import get_home
from limited.serve.manager import DownloadManager
from limited.utils import split_path
from limited.views import RenderError

logger = logging.getLogger( __name__ )


def ImagesView( request, id ):
    """
    Gallery view

    template :template:`iviewer/images.html`
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    lib_id = int( id )
    path = request.GET.get( 'p', '' )
    if FilePath.check( path, norm=True ) == False:
        logger.error( u"Files. Path check fail. home_id:{0}, path:{1}".format( lib_id, path ) )
        return RenderError( request, u"IOError, Permission denied" )

    try:
        home = get_home( request.user, lib_id )

        patharr = split_path( path )

        File = home.lib.getStorage( )
        files = []
        for item in File.listdir( path ):
            tmp = item["name"].lower( )
            if tmp.endswith( ".jpg" ) or tmp.endswith( ".jpeg" ):
                files.append( item )

        small_image = ResizeOptions( settings.LVIEWER_SMALL_IMAGE )
        big_image = ResizeOptions( settings.LVIEWER_BIG_IMAGE )
    except ObjectDoesNotExist:
        logger.error( u"Files. No such file lib or you don't have permissions. home_id:{0}, path:{1}".format( lib_id, path ) )
        return RenderError( request, u"No such file lib or you don't have permissions" )
    except FileError as e:
        logger.error( u"Files. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
        return RenderError( request, e )

    return render( request, u"lviewer/images.html", {
        'pathname': request.path,
        'path': path,
        'patharr': patharr,
        'home_id': lib_id,
        'home': home.lib.name,
        'permission': home.permission,
        'files': files,
        'small_image': small_image,
        'big_image': big_image,
        } )


def ResizeView( request, id, size ):
    """
    Resize view 
    """
    if request.user.is_anonymous( ) and not settings.LIMITED_ANONYMOUS:
        return HttpResponseRedirect( '%s?next=%s' % (settings.LOGIN_URL, request.path) )

    if request.method == u"GET":
        lib_id = int( id )
        path = request.GET.get( 'p', '' )
        if FilePath.check( path, norm=True ) == False:
            logger.error( u"Files. Path check fail. home_id:{0}, path:{1}".format( lib_id, path ) )
            return RenderError( request, u"IOError, Permission denied" )

        try:
            options = ResizeOptions( size )
            home = get_home( request.user, lib_id )
            storage = home.lib.getStorage( )
            if not storage.isfile( path ):
                raise FileNotExist()
            if not( path.endswith( ".jpg" ) or path.endswith( ".jpeg" ) ):
                raise FileNotExist()
            
            HashBuilder = FileUnicName( )
            hash_path = HashBuilder.build( path, extra=options.size )
            hash_path = FilePath.join( settings.LIMITED_CACHE_PATH, hash_path + ".jpg" )
            bigger = False
            if not storage.exists( settings.LIMITED_CACHE_PATH ):
                storage.mkdir( settings.LIMITED_CACHE_PATH )
            if not storage.exists( hash_path ):
                filein = storage.open( path, mode='rb', signal=False )
                newImage = ResizeImage( filein )
                bigger = newImage.isBigger( options.width, options.height )
                if not bigger:
                    if options.crop:
                        w, h = newImage.minSize( options.size )
                        newImage.resize( w, h )
                        newImage.cropCenter( options.width, options.height )
                    else:
                        w, h = newImage.maxSize( options.size )
                        newImage.resize( w, h )
                    fileout = storage.open( hash_path, mode='wb', signal=False )
                    newImage.saveTo( fileout )
                    fileout.close( )
                filein.close( )
            manager = DownloadManager( home.lib )
            if not bigger:
                response = manager.build( hash_path )
            else:
                response = manager.build( path )

        except ResizeOptionsError:
            raise Http404( u"Wrong resize option" )
        except ObjectDoesNotExist:
            logger.error( u"ResizeView. No such file lib or you don't have permissions. home_id:{0}, path:{1}".format( lib_id, path ) )
            return RenderError( request, u"No such file lib or you don't have permissions" )
        except FileNotExist as e:
            logger.error( u"ResizeView. No file or directory find. home_id:{0}, path:{1}".format( lib_id, path ) )
            raise Http404( u"No file or directory find" )

        return response