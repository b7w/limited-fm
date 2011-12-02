************************************
File Storage API
************************************

.. index:: File Storage API

.. index:: Intro


Intro
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