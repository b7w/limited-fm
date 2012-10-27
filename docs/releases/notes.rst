************************************
Release notes
************************************

.. index:: Release notes

| Release notes for the official Limited FM releases.
  Each release note will tell you what’s new in each version,
  and will also describe any backwards-incompatible changes made in that version.


.. index:: Release notes 1.3

1.3 release
====================================


1.3.1
------------------------------------

| Fix some strong bugs. Move error message on uploading not allowed file names
  to settings :ref:`SETTINGS_FILES_MESSAGE`. Now it can be easy to tell user where error is.

* Fix wrong message on uploading not allowed file names.
* Fix encoding problems in mail notify.
* Fix profile creation only on LUser add.


1.3.0
------------------------------------

| Fix rss bug and add email notify for new upload files.
  For this purpose was created Profile model with rss token and notify flag.
  On updating it is needed to syncdb, and feel for each user his rss token.
  :func:`limited.core.models.Profile.create_rss_token` can help.

* Fix admin error when try edit luser.
* Fix setting paths that change in django 1.4.
* Fix bug when rss available only for authenticated users.
* Fix bug when no permissions check for url upload.



.. index:: Release notes 1.2

1.2 release
====================================


1.2.0
------------------------------------

| Move application to django 1.4 framework version.
  Now it is cool static files with hashes, no any old cache on clients.
  Instead of checking file extensions add regex file name check.
  Add chmod for static files in fabfile and support for checking available libraries.
  Now message appear on bad zip file.

* Fix zip/unzip wrong method call
* Fix lviewer image detecting for upper case jpg extension
* Fix unicode error on windows like zip files
* Fix error on bad zip file.



.. index:: Release notes 1.1

1.1 release
====================================


1.1.1
------------------------------------

| Hot bug fixes. Move temporary and tests files to 'tmp' directory.
  Improve work with zip files

* Fix zip/unzip action
* Write back test for lviewer
* Fix unicode error in regex check of mkdir
* Fix lviewer image detected for upper case jpg extension
* Fix server error on bad zip files
* Fix unicode error on windows like zip files


1.1.0
------------------------------------

| Redesign file storage api, move all logic to :class:`limited.core.files.api.FileStorageApi`
  and low level functions to :class:`limited.core.files.storage.FileStorage`.
  Move :class:`~limited.core.files.utils.FilePath` to utils module.
  Add lviewer plugin to show images in pretty gallery.
  Add check for special symbols in mkdir.
  Add fab file to help build, clear an etc.

* Fix error when upload file with more than one dot
* Fix escape in file name for back slash
* Fix error on file upload without extension



.. index:: Release notes 1.0

1.0 release
====================================


1.0.3
------------------------------------

| Fix a lot of critical errors that allow to look file system.
  Make :class:`limited.core.files.api.FileStorageApi` proxy for :class:`~limited.core.files.storage.FileStorage`.
  Move hash method to new class. Now it checks and controls chrooting in file lib.

* Add :func:`limited.core.files.storage.FilePath.check` to check if path is strange
* Add safe class :class:`limited.core.files.api.FileStorageApi` all storage actions now through that wrapper

* Fix critical error listing '../' directory, when with FileLib permission user can look all FS
* Fix :func:`~limited.core.files.storage.FilePath.join` when join '/smth' and '/smth2' get '/smth2'
* Fix calling :func:`~limited.core.files.storage.FileStorage.abspath` in wrong places
* Fix adding serve cache record for files
* Fix default serve backend opening file with signal that change cache


1.0.2
------------------------------------

| Release with some fixes. Plus add image rename.png for warning messages.
  Rename History field name to files, need db update.
  Add docs for extra model fields.

* Fix Deprecation warning with get_db_prep_lookup
* Fix some server test that not run on others machines
* Fix empty history when upload no files


1.0.1
------------------------------------

| History now store all changed files in database. In ``name`` field in comma separated way.
  The filed need to be updated to 1024 max length.
  With this feature, history link following highlight all changed files.

* Fix Tread auto join after start
* Fix Upload restriction in Opera
* Fix Wrong upload names in history if the same name exists
* Fix *ObjectDoesNotExist* if try to download/upload from lib that not in users home