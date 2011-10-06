************************************
File Storage API
************************************

.. index:: File Storage API

.. index:: Intro


Intro
====================================

| At first I started looking for complete solutions.
  And standard Django storage seemed good. A lot of backend for other file systems.
  But it have too few methods. Only save and listdir.

| Than I try to write same base class for the storage.
  But with each rewrite, I realized that it is quite useless.
  So I forgot about API and just create new methods when it is needed.
  The realisation can change from version to version.


.. index:: Storage model

Storage model
====================================

| FileStorage have a lot of methods. Lets list and group them in more sorted order.

* | Creating: :func:`~limited.files.storage.FileStorage.open` |
    :func:`~limited.files.storage.FileStorage.save` |
    :func:`~limited.files.storage.FileStorage.create` |
    :func:`~limited.files.storage.FileStorage.mkdir`

* | Editing: :func:`~limited.files.storage.FileStorage.rename` |
    :func:`~limited.files.storage.FileStorage.move` |
    :func:`~limited.files.storage.FileStorage.zip` |
    :func:`~limited.files.storage.FileStorage.unzip`

* | Deleting: :func:`~limited.files.storage.FileStorage.remove` |
    :func:`~limited.files.storage.FileStorage.clear` |
    :func:`~limited.files.storage.FileStorage.totrash`

* | Check: :func:`~limited.files.storage.FileStorage.exists` |
    :func:`~limited.files.storage.FileStorage.isfile` |
    :func:`~limited.files.storage.FileStorage.isdir` |
    :func:`~limited.files.storage.FileStorage.available_name`

* | Getting: :func:`~limited.files.storage.FileStorage.listdir` |
    :func:`~limited.files.storage.FileStorage.listfiles` |
    :func:`~limited.files.storage.FileStorage.download` |
    :func:`~limited.files.storage.FileStorage.size`

* | Name: :func:`~limited.files.storage.FileStorage.abspath` |
    :func:`~limited.files.storage.FileStorage.homepath` |
    :func:`~limited.files.storage.FileStorage.url`

* | Time: :func:`~limited.files.storage.FileStorage.accessed_time` |
    :func:`~limited.files.storage.FileStorage.created_time` |
    :func:`~limited.files.storage.FileStorage.modified_time`
    

.. note:: At the moment, methods of storage may vary from version to version

| A lot of method have :obj:`limited.files.storage.file_pre_change` signal.
  By default it is turn on. It is made to invalidate cache of a directory.
  If you do something make clear that signal raise only once.

.. autoclass:: limited.files.storage.FileStorage
    :show-inheritance:
    :undoc-members:
    :members:



.. index:: Storage utils

Storage utils
====================================

| Wrapper for ``os.path`` for working with file paths.
  The class is static, no needed to create instance.
  For more utils look 'limited.files.utils' file.
  In it you can find wrappers to download and zip in a tread.
  Hash name builder for files.

.. autoclass:: limited.files.storage.FilePath
    :show-inheritance:
    :undoc-members:
    :members:



.. index:: Storage exceptions

Storage exceptions
====================================

| Some storage exceptions. All other errors are caught.

.. autoexception:: limited.files.storage.FileError
    :show-inheritance:

.. autoexception:: limited.files.storage.FileNotExist
    :show-inheritance:
