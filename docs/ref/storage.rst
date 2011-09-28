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
    :func:`~limited.files.storage.FileStorage.create` |
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

.. autoclass:: limited.files.storage.FileStorage
    :show-inheritance:
    :undoc-members:
    :members: 