************************************
File Storage API Base
************************************

.. index:: File Storage API Base

.. index:: File Storage API Base Description


Description
====================================

| FileStorageApi is abstract class for file storage.
   It has some useful static methods like url, available_name and etc



.. index:: File Storage API Base Abstract class model

Abstract class model
====================================

.. autoclass:: limited.core.files.api.base.FileStorageBaseApi
    :show-inheritance:
    :undoc-members:
    :members:

    .. method:: __init__(self, lib )
        Take :class:`limited.models.FileLib` as a parameter