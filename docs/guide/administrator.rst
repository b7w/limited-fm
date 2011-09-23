************************************
Administrator guide
************************************

.. index:: Administrator guide

.. index:: Installation guide


Installation guide
====================================

| Limited file manager base on Django framework.
  So it ease to set up and run. Application doesn't depending of external libraries.
  All you need is a web server that support fast-cgi, any DBMS including sqlite,
  python 2.5 or later ( but not v3 ).

| System tests on linux and not on others OS.
  So you may run into some difficulties.
  If you find some bugs or errors please write issue, :doc:`feedback </intro/feedback>`.
  I will try to fix them as fast as possible.

| For more detail steps you can look :ref:`here <installation>`.
  There you will find base instructions to copy source code
  and start to use application with nginx and fast-cgi.



.. index:: Better web server

Better web server
====================================

| I recommend to choose Nginx.
  You can read `here <http://nginx.org/>`__ and `here <http://wiki.nginx.org/>`__ about it.
  Nginx powers several high-visibility sites, such as
  WordPress, Hulu, Github, Ohloh, SourceForge, WhitePages and TorrentReactor.
  This web server is easily to set up, and it not so heavy as apache.
  You can install latest from `PPA <https://launchpad.net/~nginx/+archive/development>`__
  if you use Ubuntu or read `this <http://wiki.nginx.org/Install>`__ for others methods.

.. note:: Also today only nginx has backend to serve files with help of 'X-Sendfile'.



.. index:: Serve files

Serve files
====================================

| Serving file by the application is not a good idea.
  Interpreted languages not so fast and of course not optimised for it.
  It is better to delegate that work to web server.
  Most web servers are support 'X-Sendfile'.

| To set backend add to the setting file ``LIMITED_SERVE`` parameter.
  It is a dict with 'BACKEND', 'INTERNAL_URL', 'Content-Type' keys.
  Default BACKEND is ``limited.serve.backends.default``.
  It is standard django serving files.
  To delegate serving to nginx change BACKEND to 'limited.serve.backends.nginx'
  Sample setting file for nginx you can see :ref:`here <nginx_settings>`
  Also there is 'Content-Type' argument, his default value 'application/octet-stream'.
  But if set '', nginx will try to detect content-type automatic.

| Also read settings, :ref:`LIMITED_SERVE <SETTINGS_SERVE>`.



.. index:: Temporary files
.. index:: Clear folder command

Temporary files
====================================

| Application have trash folder and cache folder in all file lib.
  So we need to clear it sometimes.
  For that limited have management command.

.. code-block:: bash

    python manage.py clearfolder .TrashBin --settings=settings
    python manage.py clearfolder .cache '7*24*60*60' --settings=settings

| Clear folder command have to parameters.
  First is the path to the folder where we need to delete all data.
  And the second and optional is a time in seconds.
  If file created time is older than that value it will be deleted.
  Default it is a week. You can perform any mathematical expressions used in python.

| As you can see it is very simple to use.
  Set something like that to crontab to run it automatic every 3 hours.

.. code-block:: bash

  00 */3  * * *   root    python /path/to/manage.py clearfolder .cache --settings=settings



.. index:: Limited management

Limited management
====================================

| It is assumed that we have already installed limited and it is already running.
  And now we need to make some step. Add users, add file libs.
  Log in with administrator rights. Ang go to admin page.
  It is a link on the top right of home page or
  just enter '../admin/' in the query string.

| First let set your domain name.
  Go to ``Site`` > ``Sites`` > ``example.com`` and edit it.
  Now direct links will be displayed correctly.

| Lets add some file libs.
  Go to ``Limited`` > ``File Libs`` > ``Add File Lib``.
  Enter Name, Short description, and path from :ref:`SETTINGS_ROOT_PATH <SETTINGS_ROOT_PATH>`.
  Click ``save``. Add more if necessary.

| Now time to add users. There is two ways od do it.
  Through the standard module ``Auth`` > ``Users`` or ``Limited`` > ``Users``.
  In first you can change personal info, Django permissions, groups,
  and other things, but not limited settings.
  To add file lib to user you must go to ``Limited`` > ``Home`` > ``Add Home``.
  Select users from existing, select file lib and check permissions.
  In second you can add user, set personal info and add file libs with exiting permissions.
  
.. note:: **Limited** > **Home** > **Object**.
          If there isn't such permission in database it will be created.
          
.. note:: **Limited** > **User** > **Object**.
          Note than if you click magnifier in Home module nearby permission you see window.
          Where you can easily find permits with help of filters.



.. index:: Open access to file libs

Open access to file libs
====================================

| There is opportunity to make file libs open to anonymous users.
  All open file lib will be available to registered users too.
  They will be displayed after others.
  If registered users have the same file lib, his permission will be taken.

| In reality, to do that we just need to make special user.
  Attach file lib to him with some rights.
  And turn on this feature in settings.
  Two parameters are responsible for this.
  :ref:`LIMITED_ANONYMOUS <SETTINGS_ANONYMOUS>` and
  :ref:`LIMITED_ANONYMOUS_ID <SETTINGS_ANONYMOUS_ID>`.
  Just set first ``True`` and user id in second.

.. note:: To get user id in admin panel just click to edit user and look at query string.
          The last integer will be the user id.



.. index:: Error reporting
.. index:: Mail error reporting

Error reporting
====================================

Mail error reporting
------------------------------------

| Django framework can report server error to email.
  In sample setting file email handler already exists.
  To use it you only need set up email settings.
  Add lines below and modify it with your values.

.. code-block:: python

    EMAIL_HOST = 'smtp.mail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'user@mail.com'
    EMAIL_HOST_PASSWORD = 'secret'
    EMAIL_USE_TLS = True

| You may stop notification by deleting handler.
  Just remove from variable
  LOGGING > loggers > django.request > handlers 'mail_admins' handler.


.. index:: Logging error reporting

Logging error reporting
------------------------------------

| There is a great capabilities get logs from application.
  But it is really difficult to set up.
  So if you want to change something it better to visit
  `official logging documentation <http://docs.djangoproject.com/en/dev/topics/logging>`__.
  By default there is a 'app.log' in project directory.
  With info level.
  