************************************
Model extra fields
************************************

.. index:: Model extra fields

.. index:: Json tree field


Json tree field
====================================

| Field :class:`limited.fields.JsonTreeField` is based on :class:`~django.db.models.TextField`.
  It is a simple field to store tree in database in json format.
  In python implementation it is a :class:`limited.utils.TreeNode`.
  It is used to store file lib cache in :class:`limited.models.FileLib`.
  If field is None of empty string it return TreeNode with 'root' name and '' hash.
  :class:`~limited.fields.JsonTreeField` is going with :class:`limited.fields.JSONWidget`.

.. code-block:: python

    >>> from limited.models import FileLib
    >>> lib = FileLib.objects.get( name="Test" )
    >>> lib.cache
    <limited.utils.TreeNode instance at 0x97eda2c>
    >>> lib.cache.children
    {u'content.txt': <limited.utils.TreeNode instance at 0x97eda6c>}
    >>> lib.cache.children['content.txt'].toDict()
    {'hash': 1320216447.656839, 'name': u'content.txt', 'children': []}
    >>> lib.cache.getName( ('content.txt',) ).toDict()
    {'hash': 1320216447.656839, 'name': u'content.txt', 'children': []}
    >>> lib.cache.getName( ('content.txt',) ).hash = 0
    >>> lib.save()
    >>> lib = FileLib.objects.get( name="Test" )
    >>> lib.cache.getName( ('content.txt',) ).toDict()
    {'hash': 0, 'name': u'content.txt', 'children': []}
    >>> lib.cache.deleteName( ('content.txt',) )
    >>> lib.save()
    >>> lib = FileLib.objects.get( name="Test" )
    >>> lib.cache.getName( ('content.txt',) ) == None
    True



.. index:: Text list field

Text list field
====================================

| Field :class:`limited.fields.TextListField` is based on :class:`~django.db.models.CharField`.
  It is a simple field than store list in database as a string with separated items by ';'.
  It is used to store files in :class:`limited.models.History`.
  If items in list will be more than ``max_length`` the list will be cut and error send to log.

.. code-block:: python

    >>> from limited.models import History
    >>> h = History.objects.get(id=6)
    >>> h.name
    [u'DSC02054.jpg', u'DSC02055.jpg', u'DSC02056.jpg', u'DSC02063.jpg',]
    >>> h.name = ['1','2']
    >>> h.save()
    >>> h = History.objects.get(id=6)
    >>> h.name
    [u'1', u'2']