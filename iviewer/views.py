# -*- coding: utf-8 -*-

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from iviewer.utils import ResizeImage, ResizeOptions, ResizeOptionsError

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

    try:
        home = get_home( request.user, lib_id )

        patharr = split_path( path )

        File = home.lib.getStorage( )
        files = File.listdir( path )
        files = [i for i in files if i["name"].lower( ).endswith( ".jpg" )]
    except ObjectDoesNotExist:
        logger.error( u"Files. No such file lib or you don't have permissions. home_id:{0}, path:{1}".format( lib_id, path ) )
        return RenderError( request, u"No such file lib or you don't have permissions" )
    except FileError as e:
        logger.error( u"Files. {0}. home_id:{1}, path:{2}".format( e, lib_id, path ) )
        return RenderError( request, e )

    return render( request, u"iviewer/images.html", {
        'pathname': request.path,
        'path': path,
        'patharr': patharr,
        'home_id': lib_id,
        'home': home.lib.name,
        'permission': home.permission,
        'files': files,
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

        options = ResizeOptions( size )
        try:
            home = get_home( request.user, lib_id )
            storage = home.lib.getStorage( )

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