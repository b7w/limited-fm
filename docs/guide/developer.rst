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
  *dump.json* file is test data. *LICENSE* is a BSD license text.
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
    * | base: Base StorageTestCase for more easier test files actions.
        For more look :doc:`here </topics/testing>`.
    * | storage: Tests of FileStorage.
    * | serve: Tests of DownloadManager and his backends.
    * | actions: Some action test via web client.
    * | views: A lot of tests of views via web client.
    * | other: Tests of utils, models other small functions.

* | controls: Function that get some data from database or utils related to web.

* | utils: Some small functions.

* | settings: Module to import default settings for limited app.
    For more look :doc:`here </ref/settings>`.



What to read next
====================================

| Some links to help find out more information.
  Also look :doc:`Index </index>` and :doc:`Table of contents </contents>`

* | :doc:`/ref/models`.
* | :doc:`/ref/storage`.
