# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.db.models.query_utils import Q

from limited.core import settings
from limited.core.models import Home, History, Profile
from limited.core.utils import urlbilder


class BaseUserFeed(Feed):
    """
    Base feed for History objects
    Need to override get_object method.
    """
    title = u"User feed"
    link = u"/"
    description = u"Some history events"

    def get_object(self, request, *args, **kwargs):
        raise NotImplemented()

    def items(self, obj):
        return obj

    def item_title(self, item):
        return u", ".join(item.files)

    def item_description(self, item):
        return u"{0} by {1}, in '{2}'".format(item.get_type_display(), item.user, item.path or u'/').capitalize()

    def item_link(self, item):
        return urlbilder(u"browser", item.lib_id, p=item.path, hl=item.hash())

    def item_pubdate(self, item):
        return item.time


class UserAnonFeed(BaseUserFeed):
    """
    Feed that provide history for all libs
    """

    def get_object(self, request):
        history = []
        if settings.LIMITED_ANONYMOUS:
            homes = Home.objects.select_related('lib').filter(user=settings.LIMITED_ANONYMOUS_ID).order_by('lib__name')

            libs = [i.lib_id for i in homes]

            history = History.objects.\
                      select_related('user', 'lib').\
                      only('lib', 'type', 'files', 'path', 'extra', 'user__username', 'lib__name').\
                      filter(lib__in=libs).\
                      order_by('-time')[0:20]
        return history


class UserFeed(BaseUserFeed):
    """
    Feed that provide history for all libs
    """

    def get_object(self, request, hash):
        user = Profile.objects.get(rss_token=hash).user

        if settings.LIMITED_ANONYMOUS:
            homes = Home.objects.select_related('lib').filter(Q(user=user) | Q(user=settings.LIMITED_ANONYMOUS_ID)).order_by('lib__name')
        else:
            homes = Home.objects.select_related('lib').filter(user=user).order_by('lib__name')
        libs = [i.lib_id for i in homes]

        history = History.objects.\
                  select_related('user', 'lib').\
                  only('lib', 'type', 'files', 'path', 'extra', 'user__username', 'lib__name').\
                  filter(lib__in=libs).\
                  order_by('-time')[0:20]
        return history


class UserLibFeed(BaseUserFeed):
    """
    Feed that provide history for one lib
    """

    def get_object(self, request, hash, lib_id):
        user = Profile.objects.get(rss_token=hash).user

        count = Home.objects.select_related('lib').filter(Q(user=user) | Q(user=settings.LIMITED_ANONYMOUS_ID), lib__id=lib_id).count()
        if not count:
            raise Home.DoesNotExist()

        history = History.objects.\
                  select_related('user').\
                  only('lib', 'type', 'files', 'path', 'extra', 'user__username').\
                  filter(lib=lib_id).\
                  order_by('-id')[0:20]

        return history
