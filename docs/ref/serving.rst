************************************
Serve backend
************************************

.. index:: Serve backend


Serve files
====================================

| Serving file by the application is not a good idea.
  Interpreted languages not so fast and of course not optimised for it.
  It is better to delegate that work to web server.
  Most web servers are support 'X-Sendfile'.

| To set up read this :ref:`guide <administrator_serve_files>`.



.. index:: Base serve backend

Base serve backend
====================================

| The base backend is very simple. The main idea is to generate specific HttpResponse.
  Constructor take two parameters storage object and settings dict.
  First is needed if you want to work with files.
  Second to store something like 'content-type', be carefully it is case sensitive!
  Settings are taken from setting file, :ref:`SETTINGS_SERVE` variable.

| But main method is ``generate``. As we have said it should return HttpResponse object.
  Parameters are the path to the file and file name.
  http protocol doesn't support UTF-8 so you need to encode it. It is simple to do with python.
  Just use this ``u"file name".encode( 'utf-8' )``.
  To get file size for 'content-length' header use ``self.storage.size( path )``.
  To get full path form root directory use ``self.storage.homepath( path )``, this value also need to encode.

| Code of base class:

.. code-block:: python

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



.. index:: Sample backends
.. index:: Default backend

Sample backends
====================================

Default backend
------------------------------------

.. code-block:: python

    class default( BaseDownloadResponse ):
        def generate(self, path, name):
            wrapper = FileWrapper( self.storage.open( path ) )
            response = HttpResponse( wrapper )
            response['Content-Type'] = self.settings['Content-Type']
            response['Content-Disposition'] = "attachment; filename=\"%s\"" % name.encode( 'utf-8' )
            response['Content-Length'] = self.storage.size( path )
            return response


.. index:: Nginx backend

Nginx backend
------------------------------------

.. code-block:: python

    class nginx( BaseDownloadResponse ):
        def generate(self, path, name):
            response = HttpResponse( )
            url = self.settings['INTERNAL_URL'] + '/' + self.storage.homepath( path ).encode( 'utf-8' )
            response['X-Accel-Charset'] = "utf-8"
            response['X-Accel-Redirect'] = url
            response['Content-Type'] = self.settings['Content-Type']
            response['Content-Disposition'] = "attachment; filename=\"%s\"" % name.encode( 'utf-8' )
            return response
