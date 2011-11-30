************************************
Release notes
************************************

.. index:: Release notes

| Release notes for the official Limited FM releases.
  Each release note will tell you what’s new in each version,
  and will also describe any backwards-incompatible changes made in that version.



.. index:: Release notes 1.0

1.0 release
====================================


1.0.1
------------------------------------

| History now store all changed files in database. In ``name`` field in comma separated way.
  The filed need to be updated to 1024 max length.
  With this feature, history link following highlight all changed files.

* Fix Tread auto join after start
* Fix Upload restriction in Opera
* Fix Wrong upload names in history if the same name exists
* Fix *ObjectDoesNotExist* if try to download/upload from lib that not in users home


1.0.2
------------------------------------

| Release with some fixes. Plus add image rename.png for warning messages.
  Rename History field name to files, need db update.
  Add docs for extra model fields.

* Fix Deprecation warning with get_db_prep_lookup
* Fix some server test that not run on others machines
* Fix empty history when upload no files


1.0.3
------------------------------------

| Fix a lot of critical errors that allow to look file system.
  Make :class:`limited.files.api.FileStorageApi` proxy for :class:`~limited.files.storage.FileStorage`.
  Move hash method to new class. Now it checks and controls chrooting in file lib.

* Add :func:`limited.files.storage.FilePath.check` to check if path is strange
* Add safe class :class:`limited.files.api.FileStorageApi` all storage actions now through that wrapper

* Fix critical error listing '../' directory, when with FileLib permission user can look all FS
* Fix :func:`~limited.files.storage.FilePath.join` when join '/smth' and '/smth2' get '/smth2'
* Fix calling :func:`~limited.files.storage.FileStorage.abspath` in wrong places
* Fix adding serve cache record for files
* Fix default serve backend opening file with signal that change cache