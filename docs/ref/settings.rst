************************************
Settings
************************************

.. index:: Settings

| Default settings is hard to use. Because you can not set default value.
  So limited setting module help to fix it.
  All you need to change is import statement.
  To use settings do import like that ``from limited import settings``.
  In limited.settings not all django settings are included.

 

.. _SETTINGS_ANONYMOUS:

LIMITED_ANONYMOUS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

| If you need to allow 'Anonymous' users access to some file libs set this ``True``.
  Do not forget to create user "Anonymous" in Database and set up **LIMITED_ANONYMOUS_ID**.
  User name will be displayed in the top panel on the right for all non-registered users.
  *Also look* :ref:`SETTINGS_ANONYMOUS_ID`



.. _SETTINGS_ANONYMOUS_ID:

LIMITED_ANONYMOUS_ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``0``

| 'Anonymous' user ID for non-registered access to file lib.
  Add file libs to this user, and they will be displays for all users.
  If some user have access to file lib, his permission will be taken.
  *lso look* :ref:`SETTINGS_ANONYMOUS`



.. _SETTINGS_ROOT_PATH:

LIMITED_ROOT_PATH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``/home``

| Absolute path to file storage.
  This path will be added to file lib's path.
  This is done to reduce long full paths in the administration panel.
  Also to reduce opportunity to view any directory on your system.



.. _SETTINGS_CACHE_PATH:

LIMITED_CACHE_PATH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``.cache``

| All file lib has cache folder.
  This function are using to store big files or archive that can't be load to memcache, etc.
  This setting is local path to that folder.
  It will be add to file lib path.
  Use first char '*.*' to set in hidden.



.. _SETTINGS_TRASH_PATH:

LIMITED_TRASH_PATH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``.TrashBin``

| In all file lib files after deleting are moved to trash folder.
  This setting is local path to that folder.
  It will be add to file lib path.
  Use first char '*.*' to set in hidden.



.. _SETTINGS_LINK_MAX_AGE:

LIMITED_LINK_MAX_AGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``7 * 24 * 60 * 60``

| Time in seconds after witch link will be expired.
  Default 7 days.



.. _SETTINGS_ZIP_HUGE_SIZE:

LIMITED_ZIP_HUGE_SIZE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``32 * 1024 ** 2``

| Max size in bytes after witch serving directory will run in background.
  And user see a message to try a lit bit later.
  Default 32 megabytes.



.. _SETTINGS_ILES_ALLOWED:

LIMITED_FILES_ALLOWED
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{ 'ONLY': [], 'EXCEPT': ['rar', '7z', ], }``

| Limitation for file extensions in upload zone. It is a dict with two lists.
  Use ``ONLY`` list if you need to allowed upload only some range of extensions.
  Add extensions to ``EXCEPT`` list to block them.



.. _SETTINGS_SERVE:

LIMITED_SERVE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{ 'BACKEND': 'limited.serve.backends.default', 'INTERNAL_URL': '/protected', }``

| Backend for serving files. For this time only 2 backend supported,
  ``limited.serve.backends.default`` and ``limited.serve.backends.nginx``.
  Default is standard django serving files.
  Nginx use 'X-Sendfile', sample setting you can see :ref:`here <nginx_settings>`

| Also there is 'Content-Type' argument, his default value 'application/octet-stream'.
  But if set '', nginx will detect content-type automatic.