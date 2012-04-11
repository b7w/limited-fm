************************************
File Storage API
************************************

.. index:: File Storage API

.. index:: File Storage API Description


Description
====================================

| FileStorageApi class is height level operation on file system.
  It is control access and chrooting. Use it in all cases.

| All storage classes are extend :class:`limited.core.files.api.base.FileStorageBaseApi`
  to provide some useful static method.



.. index:: File Storage Signals

Signals
====================================

| A lot of method have :obj:`limited.core.files.api.base.file_pre_change` signal.
  By default it is turn on, parameter ``signal=True``. It is made to invalidate cache of a directory.
  If you do something make clear that signal raise only once.



.. index:: File Storage Api Methods list

Methods list
====================================

| FileStorage have a lot of methods. Lets list and group them in more sorted order.
  Be carefully not all methods are in :class:`~limited.core.files.api.FileStorageApi`.

* | Creating: :func:`~limited.core.files.api.FileStorageApi.open` |
    :func:`~limited.core.files.api.FileStorageApi.save` |
    :func:`~limited.core.files.api.FileStorageExtra.create` |
    :func:`~limited.core.files.api.FileStorageApi.mkdir`

* | Editing: :func:`~limited.core.files.api.FileStorageApi.rename` |
    :func:`~limited.core.files.api.FileStorageApi.move` |
    :func:`~limited.core.files.api.FileStorageExtra.zip` |
    :func:`~limited.core.files.api.FileStorageExtra.unzip`

* | Deleting: :func:`~limited.core.files.api.FileStorageApi.remove` |
    :func:`~limited.core.files.api.FileStorageExtra.clear` |
    :func:`~limited.core.files.api.FileStorageTrash.totrash`

* | Check: :func:`~limited.core.files.api.FileStorageApi.exists` |
    :func:`~limited.core.files.api.FileStorageApi.isfile` |
    :func:`~limited.core.files.api.FileStorageApi.isdir` |
    :func:`~limited.core.files.api.base.FileStorageBaseApi.check`

* | Getting: :func:`~limited.core.files.api.FileStorageApi.listdir` |
    :func:`~limited.core.files.api.FileStorageExtra.download` |
    :func:`~limited.core.files.api.FileStorageApi.size`

* | Name: :func:`~limited.core.files.api.base.FileStorageBaseApi.available_name`
    :func:`~limited.core.files.api.base.FileStorageBaseApi.homepath` |
    :func:`~limited.core.files.api.base.FileStorageBaseApi.hash` |
    :func:`~limited.core.files.api.base.FileStorageBaseApi.url`

* | Time: :func:`~limited.core.files.api.FileStorageApi.time`


.. index:: File Storage Api model

Storage Model
====================================

.. autoclass:: limited.core.files.api.FileStorageApi
    :show-inheritance:
    :undoc-members:
    :members:

    .. method:: __init__(self, lib )
        Take :class:`limited.core.models.FileLib` as a parameter



.. index:: File Storage Trash model

File Storage Trash model
====================================

.. autoclass:: limited.core.files.api.FileStorageTrash
    :show-inheritance:
    :undoc-members:
    :members:

    .. method:: __init__(self, lib )
        Take :class:`limited.core.models.FileLib` as a parameter



.. index:: File Storage Extra model

File Storage Extra model
====================================

.. autoclass:: limited.core.files.api.FileStorageExtra
    :show-inheritance:
    :undoc-members:
    :members:

    .. method:: __init__(self, lib )
        Take :class:`limited.core.models.FileLib` as a parameter



What to read next
====================================

| Some links to help find out more information.
  Also look :doc:`Index </index>` and :doc:`Table of contents </ref/files/index>`

* | :doc:`/ref/files/api-base`
* | :doc:`/ref/files/storage`
* | :doc:`/ref/files/utils`