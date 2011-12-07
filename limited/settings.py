# -*- coding: utf-8 -*-

from django.conf import settings

# Some default settings that needed in app
LOGIN_URL = getattr( settings, 'LOGIN_URL' )


# To allow Anonymous access
# Need user "Anonymous" in DB
LIMITED_ANONYMOUS = getattr( settings, 'LIMITED_ANONYMOUS', False )

# Anonymous user ID
LIMITED_ANONYMOUS_ID = getattr( settings, 'LIMITED_ANONYMOUS_ID', 0 )

# Absolute root BasePath to witch
# FileLib.BasePath will be added
LIMITED_ROOT_PATH = getattr( settings, 'LIMITED_ROOT_PATH', '/home' )

# Path to filelib local cache folder
LIMITED_CACHE_PATH = getattr( settings, 'LIMITED_CACHE_PATH', '.cache' )

# Path to filelib local trash folder
LIMITED_TRASH_PATH = getattr( settings, 'LIMITED_TRASH_PATH', '.TrashBin' )

# Time in seconds after witch link will be expired
LIMITED_LINK_MAX_AGE = getattr( settings, 'LIMITED_LINK_MAX_AGE', 7 * 24 * 60 * 60 )

# Max size in bytes after witch
# zipping will be async
LIMITED_ZIP_HUGE_SIZE = getattr( settings, 'LIMITED_ZIP_HUGE_SIZE', 32 * 1024 ** 2 )

# Allow and block some file extensions
LIMITED_FILES_ALLOWED = getattr( settings, 'LIMITED_FILES_ALLOWED', {
    'ONLY': [],
    'EXCEPT': ['rar', ],
} )

# Set backend for serving files
# Now only default and nginx
LIMITED_SERVE = getattr( settings, 'LIMITED_SERVE', {
    'BACKEND': 'limited.serve.backends.default',
    'INTERNAL_URL': '/protected',
} )


# Check if iViewer is loaded
LIMITED_LVIEWER = "lviewer" in settings.INSTALLED_APPS

# Limited Viewer small image size and other options
LVIEWER_SMALL_IMAGE = getattr( settings, 'LVIEWER_SMALL_IMAGE', {
    'WIDTH': 200,
    'HEIGHT': 200,
    'CROP': True,
} )

# Limited Viewer big image size and other options
LVIEWER_BIG_IMAGE = getattr( settings, 'LVIEWER_BIG_IMAGE', {
    'WIDTH': 1280,
    'HEIGHT': 720,
} )