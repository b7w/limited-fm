************************************
File Storage API
************************************

.. index:: File Storage API

.. index:: File Storage API Description


Description
====================================

| FileStorageApi class is height level operation on file system.
  It is control access and chrooting. Use it in all cases.

| All storage classes are extend :class:`limited.files.api.base.FileStorageBaseApi`
  to provide some useful static method.



.. index:: File Storage Signals

Signals
====================================

| A lot of method have :obj:`limited.files.api.base.file_pre_change` signal.
  By default it is turn on, parameter ``signal=True``. It is made to invalidate cache of a directory.
  If you do something make clear that signal raise only once.



.. index:: File Storage Api Methods list

Methods list
====================================

| FileStorage have a lot of methods. Lets list and group them in more sorted order.
  Be carefully not all methods are in :class:`~limited.files.api.FileStorageApi`.

* | Creating: :func:`~limited.files.api.FileStorageApi.open` |
    :func:`~limited.files.api.FileStorageApi.save` |
    :func:`~limited.files.api.FileStorageExtra.create` |
    :func:`~limited.files.api.FileStorageApi.mkdir`

* | Editing: :func:`~limited.files.api.FileStorageApi.rename` |
    :func:`~limited.files.api.FileStorageApi.move` |
    :func:`~limited.files.api.FileStorageExtra.zip` |
    :func:`~limited.files.api.FileStorageExtra.unzip`

* | Deleting: :func:`~limited.files.api.FileStorageApi.remove` |
    :func:`~limited.files.api.FileStorageExtra.clear` |
    :func:`~limited.files.api.FileStorageTrash.totrash`

* | Check: :func:`~limited.files.api.FileStorageApi.exists` |
    :func:`~limited.files.api.FileStorageApi.isfile` |
    :func:`~limited.files.api.FileStorageApi.isdir` |
    :func:`~limited.files.api.base.FileStorageBaseApi.check`

* | Getting: :func:`~limited.files.api.FileStorageApi.listdir` |
    :func:`~limited.files.api.FileStorageExtra.download` |
    :func:`~limited.files.api.FileStorageApi.size`

* | Name: :func:`~limited.files.api.base.FileStorageBaseApi.available_name`
    :func:`~limited.files.api.base.FileStorageBaseApi.homepath` |
    :func:`~limited.files.api.base.FileStorageBaseApi.hash` |
    :func:`~limited.files.api.base.FileStorageBaseApi.url`

* | Time: :func:`~limited.files.api.FileStorageApi.time`


.. index:: File Storage Api model

Storage Model
====================================

.. autoclass:: limited.files.api.FileStorageApi
    :show-inheritance:
    :undoc-members:
    :members:

    .. method:: __init__(self, lib )
        Take :class:`limited.models.FileLib` as a parameter



.. index:: File Storage Trash model

File Storage Trash model
====================================

.. autoclass:: limited.files.api.FileStorageTrash
    :show-inheritance:
    :undoc-members:
    :members:

    .. method:: __init__(self, lib )
        Take :class:`limited.models.FileLib` as a parameter



.. index:: File Storage Extra model

File Storage Extra model
====================================

.. autoclass:: limited.files.api.FileStorageExtra
    :show-inheritance:
    :undoc-members:
    :members:

    .. method:: __init__(self, lib )
        Take :class:`limited.models.FileLib` as a parameter



What to read next
====================================

| Some links to help find out more information.
  Also look :doc:`Index </index>` and :doc:`Table of contents </ref/files/index>`

* | :doc:`/ref/files/api-base`
* | :doc:`/ref/files/storage`
* | :doc:`/ref/files/utils`