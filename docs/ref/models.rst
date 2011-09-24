************************************
Databases models
************************************

.. index:: Databases models

.. index:: Installation guide


Permission model
====================================

| The major feature of application is Permission.
  It is a set of *BooleanField* fields to allow or disallow action for user in certain file lib.
  Permission is easy to customize and add new. Most they are mentioned in
  :func:`limited.views.ActionView` and templates.

.. autoclass:: limited.models.Permission
    :show-inheritance:
    :members:

    .. attribute:: edit

        | *BooleanField*, default ``False``.
        | Possibility to rename files and folders.

    .. attribute:: move

        | *BooleanField*, default ``False``.
        | Possibility to move files and folders.
    
    .. attribute:: delete

        | *BooleanField*, default ``False``.
        | Possibility to delete files and folders.

    .. attribute:: create

        | *BooleanField*, default ``False``.
        | Possibility to create files and folders.

    .. attribute:: upload

        | *BooleanField*, default ``False``.
        | Possibility to upload files.

    .. attribute:: http_get

        | *BooleanField*, default ``False``.
        | Possibility to download files from other resources.

| Some code examples:

.. code-block:: python

    >>> p = Permission()
    >>> p
    <Permission: IDNone: Edit False, Move False, Delete False, Create False, Upload False, Http_get False, >
    >>> p.full()
    <Permission: IDNone: Edit True, Move True, Delete True, Create True, Upload True, Http_get True, >
    >>> p.fields()
    ['edit', 'move', 'delete', 'create', 'upload', 'http_get']



.. index:: File lib  model

File lib  model
====================================

| File lib is abstraction of some folder in file system.
  Plus some other fields, such as name and description.
  The path must be specified from the :ref:`SETTINGS_ROOT_PATH <SETTINGS_ROOT_PATH>`.

.. autoclass:: limited.models.FileLib
    :show-inheritance:
    :members:

    .. attribute:: name

        | *CharField*, max_length=64, null=False.
        | Displayed name of file lib.

    .. attribute:: description

        | *CharField*, max_length=256, null=False.
        | Small description of file lib. Displayed on index page below the name.

    .. attribute:: path

        | *CharField*, max_length=256, null=False.
        | Path from :ref:`SETTINGS_ROOT_PATH <SETTINGS_ROOT_PATH>`.
          Path can start only with letters or numbers.

| Some code examples:

.. code-block:: python

    >>> FileLib
    <class 'limited.models.FileLib'>
    >>> FileLib.objects.all()
    [<FileLib: ID1: FileManager>, <FileLib: ID2: Test>]
    >>> FileLib.objects.get( name="Test" )
    <FileLib: ID2: Test>
    >>> lib = FileLib.objects.get( name="Test" )
    >>> lib.path
    u'test'
    >>> lib.get_path()
    u'/home/bw/FileManager/test'
    >>> lib.get_path( "/root" )
    u'/root/test'
    >>> lib.get_cache_size()
    0
    >>> lib.get_trash_size()
    768L