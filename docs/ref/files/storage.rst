************************************
File Storage
************************************

.. index:: File Storage

.. index:: File Storage Description


Description
====================================

| FileStorage class is low level operation on file system.
  It is not control access or chrooting. Use it only if you really need.
  In all other cases, use :class:`limited.files.api.FileStorageApi`.

| At first I started looking for complete solutions.
  And standard Django storage seemed good. A lot of backend for other file systems.
  But it have too few methods. Only save and listdir.

| Than I try to write same base class for the storage.
  But with each rewrite, I realized that it is quite useless.
  So I forgot about API and just create new methods when it is needed.
  The realisation can change from version to version.


.. index:: File Storage model

Storage model
====================================

.. autoclass:: limited.files.storage.FileStorage
    :show-inheritance:
    :undoc-members:
    :members:



.. index:: File Storage Exceptions

Exceptions
====================================

| Some storage exceptions. All other errors are caught.

.. autoexception:: limited.files.storage.FileError
    :show-inheritance:

.. autoexception:: limited.files.storage.FileNotExist
    :show-inheritance:
