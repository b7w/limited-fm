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
Need Django 1.3, MySQL
    * Really only some line depending of MySQL

# setup settings.py
cp settings.py.smpl settings.py
nano settings.py
    INSTALLED_APPS += 'limited'
    LIMITED_ANONYMOUS = True
    LIMITED_ANONYMOUS_ID = 2

# create tables
python manage.py syncdb

# collect static
python manage.py collectstatic --settings=settings

# fill permission table, optional
# generate and append 64 unic permissions
# 2^5 - edit, move, create, upload, http_get
python manage.py shell
    from limited.utils import LoadPermissions
    LoadPermissions()

# create Anonymous user if you need it
http://domain.com/admin/auth/user/add/
set him permission and file libs.

add file libs in http://domain.com/admin/limited/mfilelib/

associate members, file libs and permission you can
in http://domain.com/admin/limited/mhome/

also you can look libs per user in http://domain.com/admin/limited/luser/

[[ Test ]]

Tests better to run in sqlite without debug_toolbar and other helpers.
They can rais errors and sqlite is much faster and safer to test
just copy settings and run smth like that
    python manage.py test limited --settings=settings2