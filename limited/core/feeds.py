# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed

from limited.core import settings
from limited.core.controls import get_homes, get_home
from limited.core.models import Home, History
from limited.core.utils import urlbilder


class BaseUserFeed( Feed ):
    """
    Base feed for History objects
    Need to override get_object method.
    """
    title = "User feed"
    link = "/"
    description = "Some history events"

    def get_object(self, request, *args, **kwargs):
        raise NotImplemented( )

    def items(self, obj):
        return obj

    def item_title(self, item):
        return ", ".join( item.files )

    def item_description(self, item):
        return "{0} by {1}".format( item.get_type_display( ), item.user ).capitalize( )

    def item_link(self, item):
        return urlbilder( "browser", item.lib_id, p=item.path, hl=item.hash( ) )

    def item_pubdate(self, item):
        return item.time


class UserFeed( BaseUserFeed ):
    """
    Feed that provide history for all libs
    """

    def get_object(self, request):
        user = request.user
        Homes = get_homes( user ) or []

        libs = [i.lib_id for i in Homes]

        if not user.is_anonymous( ) and settings.LIMITED_ANONYMOUS:
            AnonHomes = Home.objects.select_related( 'lib' )\
            .filter( user=settings.LIMITED_ANONYMOUS_ID )\
            .exclude( lib__in=libs )\
            .order_by( 'lib__name' )

            for i in AnonHomes:
                if i.lib_id not in libs:
                    libs.append( i.lib_id )

        if not libs:
            raise Home.DoesNotExist( )

        history = History.objects.\
                  select_related( 'user', 'lib' ).\
                  only( 'lib', 'type', 'files', 'path', 'extra', 'user__username', 'lib__name' ).\
                  filter( lib__in=libs ).\
                  order_by( '-time' )[0:20]
        return history


class UserLibFeed( BaseUserFeed ):
    """
    Feed that provide history for one lib
    """

    def get_object(self, request, lib_id):
        history = []
        try:
            get_home( request.user, lib_id )

            history = History.objects.\
                      select_related( 'user' ).\
                      only( 'lib', 'type', 'files', 'path', 'extra', 'user__username' ).\
                      filter( lib=lib_id ).\
                      order_by( '-id' )[0:20]
        except Home.DoesNotExist:
            raise
        return history
