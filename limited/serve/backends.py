# -*- coding: utf-8 -*-

from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse

class BaseDownloadResponse:
    """
    self.settings - dict settings.LIMITED_SERVE
    plus default values such as content_type
    """

    def __init__(self, storage, settings):
        self.storage = storage
        self.settings = settings
        if not self.settings.has_key( 'Content-Type' ):
            self.settings['Content-Type'] = u"application/octet-stream"

    def generate(self, path, name):
        """
        Return HttpResponse obj.
        path and name better to encode utf-8
        """
        raise NotImplementedError( )


class nginx( BaseDownloadResponse ):
    def generate(self, path, name):
        response = HttpResponse( )
        url = self.settings['INTERNAL_URL'] + '/' + self.storage.homepath( path ).encode( 'utf-8' )
        response['X-Accel-Charset'] = "utf-8"
        response['X-Accel-Redirect'] = url
        response['Content-Type'] = self.settings['Content-Type']
        response['Content-Disposition'] = "attachment; filename=\"%s\"" % name.encode( 'utf-8' )
        return response


class default( BaseDownloadResponse ):
    def generate(self, path, name):
        wrapper = FileWrapper( self.storage.open( path, signal=False ) )
        response = HttpResponse( wrapper )
        response['Content-Type'] = self.settings['Content-Type']
        response['Content-Disposition'] = "attachment; filename=\"%s\"" % name.encode( 'utf-8' )
        response['Content-Length'] = self.storage.size( path )
        return response