************************************
Specification
************************************

.. index:: Specification

Main
====================================
* | Develop web file manage.
* | Files can be split to various *file libs*
* | Each file lib, user have some permission
* | Each user can have more then one file lib



Functional features
====================================

Users
------------------------------------
* | User authentication
* | Anonymous authentication
* | Anonymous file libs that can be available by all users
* | Administrator can see and edit all libs


File libs
------------------------------------
* | File lib points to some folder on file system
* | File lib have name and description
* | Each file lib have cache folder for large amount of data.
* | Each file lib have trash folder to provide safe delete.


Actions and permissions
------------------------------------
* | Permits doesn't depend on file system permissions
* Basic permissions:
    * edit - rename
    * | move - move file and folders.
       use */some/path* to mark path start from root directory,
       use *some/path* to mark path start from current directory,
       use *../path* to step back to the parent directory.
    * create - create new folder
    * upload - multiple file upload, with the aid of html5.
    * http_get - download files wia http protocol from other resources. make it in background.
* | Download file or directory. Directory have to be archived.
    If file lib available user can download it.
* | Links that free of permission and have max age.
    It means that every user can download file or directory in any file lib.
    If file lib available user can create link.
* | Size of a directory calculated as required and it cached.
    Available for all user.



Appearance
====================================

File table
------------------------------------
* | Row contain: file name, actions, size, modified time.
* | Name can't be longer than some value.
    If it longer than trim it and add *'..'* to the end.
    If file name have extension, save it.
* | Actions are in separate column in the form of images.
* | On delete appear *confirm* dialog.
* | On move and rename appear *prompt* dialog.


Information
------------------------------------
* | After action appear message with positive result or an error.
* | Widgets with about/info, upload, history, create and etc.



Other
====================================
* | Create tests
* | Create FAQ page
* | Create documentation
* | Licensed under the BSD license
