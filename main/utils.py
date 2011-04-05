import os
import re

from django.core.files.storage import get_storage_class
from django.conf import settings

class FileIterWrapper( object ):
    def __init__(self, flo, chunk_size=1024 ** 2):
        self.flo = flo
        self.chunk_size = chunk_size

    def next(self):
        data = self.flo.read( self.chunk_size )
        if data:
            return data
        else:
            raise StopIteration

    def __iter__(self):
        return self


# Get Storage object
#  depending on path
# example: smb:/home/user
#  or /home/user for default
def get_storage( path ):
    # 'type:', 'type', 'path'
    n, type, path = re.match( r"((\w+):)?(.*)", path ).groups( 'default' )
    cls = get_storage_cls( type )
    return cls( location=path, base_url='' )


# Find storage class by type
# default type = 'default'
#  geting from settings.DEFAULT_FILE_STORAGE
# types and backends getting from settings.FM_STORAGS
def get_storage_cls( type='default' ):
    if type == 'default':
        return get_storage_class( )

    if type in settings.STORAGES:
        import_path = settings.FM_STORAGS[type]
        return get_storage_class( import_path )
    else:
        raise NotImplemented( "For '%s' storage is not found any backends" % type )

# Split path for folders name
# with path fot this name
#   example: /root/path1/path2
#       root:/root, path1:/root/path2, path2:/root/path1/path2
def split_path( path ):
    def __split_path( path, data ):
        name = os.path.basename( path )
        if name != '':
            newpath = os.path.dirname( path )
            data = __split_path( newpath, data )
            data.append( (name, path) )
            return data
        return data

    return __split_path( path, [] )