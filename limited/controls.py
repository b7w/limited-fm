# -*- coding: utf-8 -*-
import logging
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.query_utils import Q

from limited.models import Home, FileLib, Permission
from limited.storage.base import FileStorage


logger = logging.getLogger(__name__)

def get_home( user, lib_id ):
    """
    Get Home plus related FileLib
    depending on is_authenticated or not
    and LIMITED_ANONYMOUS
    """
    if user.is_authenticated( ):
        if user.is_superuser:
            home = Home()
            home.lib = FileLib.objects.get( id=lib_id )
            home.permission = Permission.Full()
            return home
        elif settings.LIMITED_ANONYMOUS:
            home = Home.objects.select_related( 'lib', 'permission' ).\
                filter(Q(user=user) | Q(user=settings.LIMITED_ANONYMOUS_ID), lib__id=lib_id)
            length = len(home)
            if length == 0:
                raise Home.DoesNotExist
            # if len==2 than we have Anon and User permission
            # so we need to get User once
            elif length == 2:
                if home[0].user_id == settings.LIMITED_ANONYMOUS_ID:
                    return home[1]
                # else: return home[0]
            return home[0]
        else:
            return Home.objects.select_related( 'lib', 'permission' ).get( user=user, lib__id=lib_id )

    elif user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return Home.objects.select_related( 'lib' ).get( user=settings.LIMITED_ANONYMOUS_ID, lib__id=lib_id )


def get_homes( user ):
    """
    Get Home plus related FileLib
    depending on is_authenticated or not
    and LIMITED_ANONYMOUS
    """
    if user.is_authenticated( ):
        if user.is_superuser:
            homes = []
            libs = FileLib.objects.all( ).distinct( )
            for item in libs:
                homes.append( Home( lib=item ) )
            return homes
        else:
            return Home.objects.select_related( 'lib' ).filter( user=user )
    elif user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return Home.objects.select_related( 'lib' ).filter( user=settings.LIMITED_ANONYMOUS_ID )


def get_user( user ):
    """
    Return normal User obj for anon
    """
    if user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
        return User.objects.get( id=settings.LIMITED_ANONYMOUS_ID )
    return user


def truncate_path( str, length=64, ext=False):
    """
    Truncate long path. if ext=True the path extensions will not deleted

    long name.ext -> {length}...ext
    or if fail long name - {length}..
    """
    if ext == True:
        restr = r"^(.{%s}).*\.(\w+)$" % length
        name_ext = re.match( restr, str )
        if name_ext != None:
            #return "%s..%s" % name_ext.groups( )
            filename = name_ext.group(1).strip()
            fileext = name_ext.group(2).strip()
            return u"{0}..{1}".format( filename, fileext )
    if len(str) < length:
        return str
    else:
        return str[:length].strip() + u".."


def clear_folders( path, older=7 * 24 * 60 * 60 ):
    """
    Clear objects in ``path`` in all filelibs,
    older than one week by default.

    if no folder, nothing will happened
    """
    for lib in FileLib.objects.all( ):
        storage = FileStorage( lib.get_path( ) )
        if storage.isdir( path ):
            storage.clear( path, older=older )
