# -*- coding: utf-8 -*-

import os
import urllib

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote


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

    return _split_path( path, [] )


def load_permissions( using=None ):
    """
    Enumerate and create all permissions
    For any count of columns in Permission
    """
    from limited.models import Permission

    fields = Permission.fields()
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


class TreeNode:
    """
    Simple key value tree for store directories hashes in database.
    This hashes needed to know file of cache.
    """
    def __init__(self, name, hash ):
        self.name = name
        self.hash = hash
        self.parent = None
        self.children = []

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
        self.children.append( node )

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
        if args[0] == '':
            return self
        for item in self.children:
            if item.name == args[0]:
                if args.__len__() == 1:
                    return item
                return item.getName( *args[1:] )

    def createName(self, hash, *args ):
        """
        Create nodes where ``args`` is list of names and ``hash`` hash for all nodes.
        If node exists only hash will be changed.
        """
        self.hash = hash
        node = None
        for item in self.children:
            if item.name == args[0]:
                node = item

        if node == None:
            node = TreeNode( args[0], hash )
            self.setChild( node )
        if args.__len__() != 1:
            node.createName( hash, *args[1:] )
        else:
            # we not enter to the last so we need set hash manually
            node.hash = hash

    def toDict(self):
        """
        Serialise TreeNode to DictType.
        """
        children = [ i.toDict() for i in self.children ]
        data = { "name": self.name, "hash": self.hash, "children": children, }
        return data

    def __str__(self):
        return "TreeNode({0}, {1})".format(self.name, self.hash)