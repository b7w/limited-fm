# -*- coding: utf-8 -*-

import logging
import os
import re
import threading
import urllib

from django.core.mail import send_mass_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote

from limited.core import settings
from limited.core.files.utils import FilePath

logger = logging.getLogger( __name__ )

class HttpResponseReload( HttpResponse ):
    status_code = 302

    def __init__(self, request):
        HttpResponse.__init__( self )
        referer = request.META.get( u"HTTP_REFERER" )
        self[u"Location"] = iri_to_uri( referer or "/" )


def split_path( path ):
    """
    Split path for folders name
    with path fot this name

    Example::

        /root/path1/path2 ->
        root:/root, path1:/root/path2, path2:/root/path1/path2
    """

    def _split_path( path, data ):
        name = os.path.basename( path )
        if name != '':
            newpath = os.path.dirname( path )
            data = _split_path( newpath, data )
            data.append( (name, path) )
            return data
        return data

    return _split_path( FilePath.norm( path ), [] )


def url_params( **kwargs ):
    """
    Create string with http params

    Sample usage::

        from id=1,name='user',..
        to   ?id=1&name=user
    """
    str = None
    for key, val in kwargs.items( ):
        if not str: str = '?'
        else: str += '&'
        str += u"%s=%s" % (key, urlquote( val ))

    return str


def urlbilder( name, *args, **kwargs ):
    """
    Create link with http params

    Sample usage::

        from name,id=1,name='user',..
        to   /url/name/../?id=1&name=user
    """
    if kwargs:
        return reverse( name, args=args ) + url_params( **kwargs )
    else:
        return reverse( name, args=args )


def url_get_filename( url ):
    """
    Get tail without ?,=,& and try it to decode to utf-8
    or get domain name if break
    """
    result = ''
    try:
        url = iri_to_uri( url )
        # convert to acii cose urllib is shit
        bits = str( url ).split( '/' )
        names = [x for x in bits if x != '']
        # delete none useful chars
        for ch in names[-1]:
            if ch not in ('?', '=', '&',):
                result += ch
        result = urllib.url2pathname( result ).decode( 'utf-8' )

    except Exception as e:
        # set name as domen
        result = url.split( '/' )[1]

    return result


def check_file_name( value ):
    """
    Check patterns in settings.LIMITED_FILES_ALLOWED
    :param value: file name
    :return: True or False
    """
    for check in settings.LIMITED_FILES_ALLOWED['ONLY']:
        if not re.match( check, value ):
            return False
    for check in settings.LIMITED_FILES_ALLOWED['EXCEPT']:
        if re.match( check, value ):
            return False
    return True


class TreeNode:
    """
    Simple key value tree for store directories hashes in database.
    This hashes needed to know file of cache.
    """

    def __init__(self, name, hash ):
        self.name = name
        self.hash = hash
        self.parent = None
        self.children = {}

    @staticmethod
    def build( data ):
        """
        Parse and Build tree from DictType
        """
        name = data["name"]
        hash = data["hash"]
        children = data["children"]
        tree = TreeNode( name, hash )
        for item in children:
            child = TreeNode.build( item )
            tree.setChild( child )
        return tree

    def setParrent(self, node ):
        """
        Set for this node parent
        """
        self.parent = node

    def setChild(self, node ):
        """
        Add child and set him parent
        """
        node.setParrent( self )
        self.children[node.name] = node

    def setHash(self, hash ):
        """
        Change hash for this node and all parents
        """
        self.hash = hash
        if self.parent != None:
            self.parent.setHash( hash )

    def getName(self, *args ):
        """
        Get node where ``args`` is list of names.
        If ``args`` is '' than return self.
        """
        arg = args[0]
        if arg == '':
            return self
        if self.children.has_key( arg ):
            item = self.children.get( arg )
            if args.__len__( ) == 1:
                return item
            return item.getName( *args[1:] )

    def createName(self, hash, *args ):
        """
        Create nodes where ``args`` is list of names and ``hash`` hash for all nodes.
        If node exists only hash will be changed.
        """
        self.hash = hash
        node = self.children.get( args[0], None )

        if node == None:
            node = TreeNode( args[0], hash )
            self.setChild( node )
        if args.__len__( ) != 1:
            node.createName( hash, *args[1:] )
        else:
            # we not enter to the last so we need set hash manually
            node.hash = hash

    def deleteName(self, name):
        """
        Delete recursive all children
        """
        node = self.children.get( name )
        if len( node.children ) > 0:
            for item in node.children.values( ):
                node.deleteName( item.name )
        del self.children[name]

    def toDict(self):
        """
        Serialise TreeNode to DictType
        """
        children = [i.toDict( ) for i in self.children.values( )]
        data = {"name": self.name, "hash": self.hash, "children": children, }
        return data

    def __str__(self):
        return "TreeNode({0}, {1})".format( self.name, self.hash )


class MailFileNotify( threading.Thread ):
    """
    Simple Thread class that send emails.
    Default subject and user_from are take from settings.LIMITED_EMAIL_NOTIFY

    Need to set ``title``, ``body``, ``user_from`` fields.
    Emails are retrieve from ``users`` id list later in tread.
    Or you can set in directly in ``emails`` field.
    Also if ``files`` is set, they will be add to body.
    """

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super( MailFileNotify, self ).__init__( group, target, name, args, kwargs, verbose )
        self.title = settings.LIMITED_EMAIL_NOTIFY['TITLE']
        self.user_from = settings.LIMITED_EMAIL_NOTIFY['USER_FROM']
        self.body = ''
        self.users = []
        self.emails = []
        self.files = []

    def run(self):
        assert self.title and self.body and self.user_from
        if self.files:
            self.body += u'\n'
            self.body += u'Files:\n'
            self.body += u'\n'.join(map(lambda x: u' * ' + x, self.files))
        try:
            emails = self.emails or self.get_emails()
            data = [(self.title, self.body, self.user_from, (email,),) for email in emails]
            send_mass_mail(data, fail_silently=False)
        except Exception as e:
            logging.error(e)

    def get_emails(self):
        from limited.core.models import Profile
        profiles = Profile.objects.filter(user__in=self.users, mail_notify=True).exclude(user__email='').select_related('user')
        return [i.user.email for i in profiles]