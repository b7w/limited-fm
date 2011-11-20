************************************
Developer guide
************************************


.. index:: Developer guide

.. index:: Limited structure


Limited structure
====================================

| LimitedFM is generated Django structure. There are *docs* directory with documentation,
  *limited* app with main code and *templates* directory.
  Documentation is in `Sphinx <http://sphinx.pocoo.org/>`__ format.
  You can build it with ``make html`` in *docs* dir.
  For more look `here <http://sphinx.pocoo.org/contents.html>`__.
  *settings.py.smpl* sample configuration file.
  *urls.py* provide basic Django auth with limited templates, admin site, and limited url module.

| More interesting is *limited* app. Except standard templates, templatetags, management.
  In folder *files* storage class and some utils for it are exists.
  In folder *serve* file serve classes and backends for it.
  Tests are moved to *test* folder. Because there are a lot of test and it is easy to navigate.
  But from this time you can not run separate class or methods.

| Lets look more deeply:

* files:
    * | storage: FileStorage class, some exceptions and FilePath.
        For more look :doc:`here </ref/storage>`.
    * | utils: Some thread wrapper for FileStorage methods.

* management:
    * | clearfolder: Management command for delete all files from folder. Can check files for last modified.
    * | loadpermissions: Generate all permissions for model.Permission.
        For more look :ref:`here <installation_loadpermissions>`.

* serve:
    * | manager: DownloadManager for serve files with different web servers.
    * | backends: Backends for servers.
        For more look :doc:`here </ref/serving>`.

* serve:
    * | css: One css file that based on Django admin.
    * | img: Small icons for actions.
    * | js: jQuery 1.5 min and some js for actions.
    * | favicon: Just limited icon.

* templates:
    * | base: Base template with main.css and jQuery, auth panel, breadcrumbs, message list.
    * | index: Main page with some widgets and list of file libs.
    * | login: Login form in limited style.
    * | files: Table of files and directories.
    * | history: Table of history.
    * | trash: Table of deleted files and directories.
    * | error: Error page with some widgets.
    * | includes: Directory with some widgets like history and info.
        Plus body of table to render *no items*.

* templatetags:
    * | limited_filters: Some helpers. Truncate path, join path.

* tests:
    * | data: Init data for tests. It is more cross platform and easy to manage.
    * | base: Base StorageTestCase for more easier test files actions.
        For more look :doc:`here </topics/testing>`.
    * | storage: Tests of FileStorage.
    * | serve: Tests of DownloadManager and his backends.
    * | actions: Some action test via web client.
    * | views: A lot of tests of views via web client.
    * | other: Tests of utils, models other small functions.

* | controls: Function that get some data from database or utils related to web.

* | fields: Some extra Model fields and widgets.

* | utils: Some small functions.

* | settings: Module to import default settings for limited app.
    For more look :doc:`here </ref/settings>`.



.. index:: How folder cache works

How folder cache works
====================================

| There is some magic about folder cache.
  If in sub directories something changed we need to invalidate cache.
  But we can't delete it because someone can work with it.
  So we have to create one more with another key.
  For this hack in :class:`~limited.models.Filelib` we have ``cache`` filed.
  It is a three of folder names in json. In python field represented :class:`limited.utils.TreeNode`.
  Main idea is when we update key for directory we need to set this key for all parents.
  :class:`~limited.serve.manager.DownloadManager` concatenate path with key and get cache file.
  If there is no cache it will be created.



What to read next
====================================

| Some links to help find out more information.
  Also look :doc:`Index </index>` and :doc:`Table of contents </contents>`

* | :doc:`/ref/models`.
* | :doc:`/ref/storage`.
