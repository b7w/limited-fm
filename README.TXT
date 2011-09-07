###########################
#  Limited File Manager   #
###########################

[[ About ]]
It is a simple file manager.
it is support base action limitations:
    edit - rename
    move - move file and folders
    create - create new folded
    upload - multiple file upload ( provide by html5 )
    http_get - download files wia http protocol
also manager can zip/unzip and create direct link that free of permission.

Limited can manage various file libs for each user with specified permission,
plus Anonymous libs if turn on and in database created special user.
if User have the some lib as Anonymous, the Users permissions will be taken.

Super user can view and edit all libs.

File manager have simple history and Trash bin.
Trash bin stored in ".TrashBin" and created automatic.
All deleted file first move to trash.


[[ Installation ]]
Need Django 1.3

# setup settings.py
cp settings.py.smpl settings.py
nano settings.py
# and edit it

# default settings, for more look settings.py.smpl
    LIMITED_ANONYMOUS = True
    LIMITED_ANONYMOUS_ID = 2
    LIMITED_ROOT_PATH = "/home/{user}"
    LIMITED_CACHE_PATH = ".cache"
    LIMITED_TRASH_PATH = ".TrashBin"
    LIMITED_LINK_MAX_AGE = 7 * 24 * 60 * 60
    LIMITED_ZIP_HUGE_SIZE = 32 * 1024**2

# create tables
python manage.py syncdb --settings=settings

# collect static
python manage.py collectstatic --settings=settings

# fill permission table, optional
# generate and append 64 unic permissions
# 2^5 - edit, move, create, upload, http_get
python manage.py loadpermissions

# create Anonymous user if you need it
http://domain.com/admin/auth/user/add/
set him permission and file libs.

add file libs in http://domain.com/admin/limited/filelib/

associate members, file libs and permission you can
in http://domain.com/admin/limited/home/

also you can look libs per user in http://domain.com/admin/limited/user/

[[ Management ]]
# All deleted file are moved to trash - `.TrashBin`
# so if you need to clear it up, use this
python manage.py clearfolder .TrashBin '24*60*60'

# Also you need to clear `.cache` folder,
# where zip folders are stored


[[ Serve files ]]

Some folders can be rather big to zip and serve on a fly
So there is a a max folder size
after witch processing will be in a thread
and user will get a message to come later. size in bytes.

LIMITED_ZIP_HUGE_SIZE = 32 * 1024**2

Serving files with django is hard work.
Limited can tell http server to serve files

Now only nginx is available. To config it, add smth like this
location /protected {
    internal;
    alias settings.LIMITED_ROOT_PATH;
}

and in settings

LIMITED_SERVE = {
    'BACKEND': 'limited.serve.backends.nginx',
    'INTERNAL_URL': '/protected',
}

* this work only in debug=False,
* because django don't no nothing about /protected url

Also you can add 'Content-Type' in this setting.
default is 'application/octet-stream'


[[ Test ]]

Tests better to run in sqlite without debug_toolbar and other helpers.
They can rais errors and sqlite is much faster and safer to test
just copy settings and run smth like that
    python manage.py test limited --settings=settings2