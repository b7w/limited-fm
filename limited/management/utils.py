# -*- coding: utf-8 -*-
import time

from limited.models import FileLib, Permission


def load_permissions( using=None ):
    """
    Enumerate and create all permissions
    For any count of columns in Permission
    """

    fields = Permission.fields( )
    count = len( fields )
    last = count - 1
    rng = range( count )
    data = [0 for x in rng]

    for i in range( 2 ** count ):
        Pemm = Permission( )
        for l in range( count ):
            setattr( Pemm, fields[l], data[l] )
        Pemm.save( using=using )

        data[last] += 1
        for j in reversed( rng ):
            if data[j] == 2:
                data[j] = 0
                data[j - 1] += 1


def clear_folders( path, older=7 * 24 * 60 * 60 ):
    """
    Clear objects in ``path`` in all :class:`~limited.models.FileLib`,
    older than one week by default.

    if no folder, nothing will happened
    """
    for lib in FileLib.objects.all( ):
        storage = lib.getStorage( )
        if storage.isdir( path ):
            storage.extra.clear( path, older=older )


def clear_db_cache( older=7 * 24 * 60 * 60 ):
    """
    Clear database cache in :class:`~limited.models.FileLib`,
    older than one week by default.
    """

    def _tree( node ):
        for item in node.children.values( ):
            if time.time( ) - item.hash > older:
                node.deleteName( item.name )
            elif len( item.children ) > 0:
                _tree( item )

    for lib in FileLib.objects.all( ):
        _tree( lib.cache )
        lib.save( )

