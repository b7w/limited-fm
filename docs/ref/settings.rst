************************************
Settings
************************************

.. index:: Settings

| Default settings is hard to use. Because you can not set default value.
  So limited setting module help to fix it.
  All you need to change is import statement.
  To use settings do import like that ``from limited.core import settings``.
  In limited.settings not all django settings are included.

 

.. _SETTINGS_IVIEWER:

LIMITED_LVIEWER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``False``

| It is not a setting, it is a dynamic option. You don't need to set this variable.
  Option check if "iviewer" in **INSTALLED_APPS**.
  If ``True`` special url paterns will be loaded and link to gallery appear in files view.

.. note:: Need at least 2 jpg file in folder.



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



.. _SETTINGS_FILES_ALLOWED:

LIMITED_FILES_ALLOWED
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{ 'ONLY': [ u'^[А-Яа-я\w\.\(\)\+\- ]+$', ], 'EXCEPT': [ u'.+\.rar', ], }``

| Regex limitation for file names in upload, create, rename zones. It is a dict with two lists.
  Use ``ONLY`` list if you need to allowed upload only some range of patterns.
  Add extensions to ``EXCEPT`` list to block them. It is highly needed to set pattern in unicode!



.. _SETTINGS_FILES_MESSAGE:

LIMITED_FILES_MESSAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``u"This name of file '{0}' is not allowed for upload!"``

| Message to show if file is not allowed for upload. Look :ref:`SETTINGS_FILES_ALLOWED`.
  Put '{0}' for place of file name. Be careful, string must be unicode.




.. _SETTINGS_SERVE:

LIMITED_SERVE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{ 'BACKEND': 'limited.core.serve.backends.default', 'INTERNAL_URL': '/protected', }``

| Backend for serving files. For this time only 2 backend supported,
  ``limited.core.serve.backends.default`` and ``limited.core.serve.backends.nginx``.
  Default is standard django serving files.
  Nginx use 'X-Sendfile', sample setting you can see :ref:`here <nginx_settings>`

| Also there is 'Content-Type' argument, his default value 'application/octet-stream'.
  But if set '', nginx will detect content-type automatic.



.. _SETTINGS_EMAIL_NOTIFY:

LIMITED_EMAIL_NOTIFY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{ 'ENABLE': False, 'TITLE': 'LimitedFM Notify message', 'USER_FROM': 'root@localhost', }``

| LimitedFM can notify about upload files via email.
  To turn it on you need to set `ENABLE`: True and change subject and user.
  In user profile flag ``limited.core.models.Permission.mail_notify`` have to be True.
  Also you need to setup `django email options <https://docs.djangoproject.com/en/dev/ref/settings/#email-backend>`__.



.. _SETTINGS_SMALL_IMAGE:

LVIEWER_SMALL_IMAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{ 'WIDTH': 200, 'HEIGHT': 200, 'CROP': False, }``

| Limited Viewer small image size and crop options, that used in picture preview.
  By default crop is turn on. This makes the picture more lined.
  Crop option can be omitted and set by default false.
  If crop option is false, image will be resized so that would be fully fit in the width and height.



.. _SETTINGS_BIG_IMAGE:

LVIEWER_BIG_IMAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{ 'WIDTH': 1280, 'HEIGHT': 720, 'CROP': False, }``

| Limited Viewer big image size and crop options, that used in full picture.
  Crop option can be omitted and set by default false.
  If crop option is false, image will be resized so that would be fully fit in the width and height.