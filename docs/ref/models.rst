************************************
Databases models
************************************

.. index:: Databases models

.. index:: Permission model


Permission model
====================================

| The major feature of application is Permission.
  It is a set of *BooleanField* fields to allow or disallow action for user in certain file lib.
  Permission is easy to customize and add new. Most they are mentioned in
  :func:`limited.views.ActionView` and templates.

.. note:: When new objects are created it is needed to store the lowest value of Permission.
          So it is highly recommended to set permit with ID1 minimal permissions.

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

    >>> from limited.models import Permission
    >>> p = Permission()
    >>> p
    <Permission: IDNone: Edit False, Move False, Delete False, Create False, Upload False, Http_get False, >
    >>> p.full()
    <Permission: IDNone: Edit True, Move True, Delete True, Create True, Upload True, Http_get True, >
    >>> p.fields()
    ['edit', 'move', 'delete', 'create', 'upload', 'http_get']



.. index:: File lib model

File lib model
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

    >>> from limited.models import FileLib
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



.. index:: Home model

Home model
====================================

| Home is a object that binds User with file lib and permission for it.
  To get file libs of user we need to select libs where user equals.
  And then anonymous libs except we already select.
  Also it is better to use ``select_related( 'lib', 'permission' )``
  not to generate a lot of small queries.

.. autoclass:: limited.models.Home
    :show-inheritance:
    :members:

    .. attribute:: user

        | *ForeignKey* to User.
        | Store id of user

    .. attribute:: lib

        | *ForeignKey* to FileLib.
        | Store id of file lib

    .. attribute:: permission

        | *ForeignKey* to Permission, default=1.
        | Store permission id.

| Some code examples:

.. code-block:: python

    >>> from limited.models import Home
    >>> h = Home.objects.get( id=1 )
    >>> h
    <Home: ID1: lib 1, permission 5>
    >>> h.user
    <User: Anonymous>
    >>> h.lib
    <FileLib: ID1: FileManager>
    >>> h.permission
    <Permission: ID5: Edit False, Move False, Delete False, Create True, Upload False, Http_get False, >
    >>> Home.objects.select_related( 'lib' ).filter( user=3 )
    [<Home: ID2: lib 2, permission 64>]
    >>> Home.objects.select_related( 'lib' ).filter( user=2 ).exclude( lib__in=[2,] )
    [<Home: ID1: lib 1, permission 5>]



.. index:: History model

History model
====================================

| History is a simple log. It is needed to provide :ref:`recent actions <user_guide_widgets_history>`
  :ref:`history page <user_guide_history_page>`.

.. autoclass:: limited.models.History
    :show-inheritance:
    :members:

    .. attribute:: user

        | *ForeignKey* to User.
        | Store id of user

    .. attribute:: lib

        | *ForeignKey* to FileLib.
        | Store id of file lib

    .. attribute:: type

        | *IntegerField*, max_length=1, choices=ACTION
        | Type of ACTION. In range of 'create', 'upload', 'rename', 'move', 'trash', 'delete', 'link'.
          You can call all this action like attributes in upper case. For example ``History.CREATE``.
          It will be useful to create new objects.

    .. attribute:: name

        | *CharField*, max_length=256, null=False
        | Store file name or message when there is more then one files.

    .. attribute:: path

        | *CharField*, max_length=256, null=False, blank=True
        | Store path to the directory where action took place.

    .. attribute:: extra

        | *CharField*, max_length=256, null=True, blank=True
        | Store extra information. For example for link it will be a hash. Or null.

    .. attribute:: time

        | *DateTimeField*, auto_now_add=True, null=False
        | Store time when action happened.

| Some code examples:

.. code-block:: python

    >>> from limited.models import History
    >>> h = History.objects.get( id=1 )
    >>> h
    <History: ID1: B7W, ID2: Test>
    >>> h.user
    <User: B7W>
    >>> h.lib
    <FileLib: ID2: Test>
    >>> h.type
    2L
    >>> h.get_type_display()
    u'upload'
    >>> History.UPLOAD
    2
    >>> h.name
    u'\u0424\u043e\u0442\u043e 007.bin'
    >>> h.path
    u''
    >>> h.extra
    >>> h.time
    datetime.datetime(2011, 6, 26, 15, 12, 59)
    >>> h.get_image_type()
    'create'
    >>> h.is_extra()
    False
    >>> h = History.objects.get( id=3 )
    >>> h.is_extra()
    True
    >>> h.get_extra()
    u'<a href="/link/d89d9baa47e8/">direct link</a>'



.. index:: Link model

Link model
====================================

| Link is a feature to make direct link that free of permission.
  So you can share this link with anyone.
  Also link have expires date to invalidate link.
  It is made for more safety. Default age :ref:`LIMITED_LINK_MAX_AGE <SETTINGS_LINK_MAX_AGE>`.
  This model have a little bit supplemented Manager.
  LinkManager support easier add method and find by hash.

.. autoclass:: limited.models.LinkManager
    :show-inheritance:
    :members:

.. autoclass:: limited.models.Link
    :show-inheritance:
    :members:

    .. attribute:: hash

        | *CharField*, max_length=12, null=False
        | Store unique by hash and time value to find file path.

    .. attribute:: lib

        | *ForeignKey*, to FileLib.
        | Store id of file lib

    .. attribute:: path

        | *CharField*, max_length=256, null=False
        | Store path to the directory where action took place.

    .. attribute:: expires

        | *CharField*, max_length=256, null=False
        | Store expires time. Default it is creation time plus
          :ref:`LIMITED_LINK_MAX_AGE <SETTINGS_LINK_MAX_AGE>`

    .. attribute:: time

        | *DateTimeField*, auto_now_add=True, null=False
        | Store creation time.

| Some code examples:

.. code-block:: python

    >>> from limited.models import Link
    >>> l = Link()
    >>> l = Link.objects.get( id=1 )
    >>> l
    <Link: ID1: Фото 007.bin, 2011-06-29 19:56:04>
    >>> l.hash
    u'd89d9baa47e8'
    >>> l.lib
    <FileLib: ID2: Test>
    >>> l.path
    u'\u0424\u043e\u0442\u043e 007.bin'
    >>> l.expires
    datetime.datetime(2011, 6, 30, 19, 56, 4)
    >>> l.time
    datetime.datetime(2011, 6, 29, 19, 56, 4)
    >>> Link.objects.find( u'd89d9baa47e8' )
    >>> l2 = Link.objects.add( l.lib, "Test folder" )
    >>> l2
    <Link: ID3: Test folder, 2011-09-25 09:01:23.885668>
    >>> l2.hash
    '05b0b5cfee45'
    >>> Link.objects.find( '05b0b5cfee45' )
    <Link: ID3: Test folder, 2011-09-25 09:01:23>



.. index:: LUser model

LUser model
====================================

| LUser is a proxy for Django User model.
  It is made for admin panel.
  With some inlines to display user file libs and permissions.
  For more look :class:`limited.admin.AdminUser`.