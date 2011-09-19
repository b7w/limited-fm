# -*- coding: utf-8 -*-

import time

from django.test import TestCase

from limited import settings
from limited.models import FileLib
from limited.files.storage import FileStorage

# It can happen so that error in test
# are raises because of not enough time
# to wait async task.
# So increase this value
DEFAULT_SLEEP_TINE = 1.0

class Timer:
    """
    Wrapper to get sleep method
    with default value
    for waiting async tasks
    """

    def __init__(self, default=None):
        """
        default - default value in float
        """
        if default:
            self.default = default
        else:
            self.default = 1.0

    def sleep(self, times=1 ):
        """
        Sleep times * default value
        """
        time.sleep( self.default * times )


class StorageTestCase( TestCase ):
    """
    Base class to init test data in every tests.

    It creates 'test' folder in LIMITED_ROOT_PATH with
    '.TrashBin/Crash Test'
    'Test Folder'
    'content.txt' - Test line in file
    'Фото 007.bin'

    class doesn't delete test data!

    It is run always with '--failfast' option

    Best way is to test ``create``, ``mkdir`` and ``clear``
    by your own separately
    """
    fixtures = ['dump.json']

    def setUp(self):
        self.timer = Timer( DEFAULT_SLEEP_TINE )
        self.lib = FileLib.objects.get( name="Test" )
        self.storage = FileStorage( self.lib.get_path( ), self.lib.path )
        try:
            if self.storage.exists( u"" ):
                self.storage.remove( u"" )
            self.storage.mkdir( u"" )
            self.storage.mkdir( settings.LIMITED_TRASH_PATH )
            self.storage.mkdir( settings.LIMITED_TRASH_PATH + u"/Crash Test" )
            self.storage.mkdir( settings.LIMITED_CACHE_PATH )
            self.storage.mkdir( u"Test Folder" )
            self.storage.create( u"content.txt", u"Test line in file" )
            self.storage.create( u"Фото 007.bin", "007" * 2 ** 8 )
        except Exception:
            raise Exception( u"Error happened while init test files in 'setUp'" )

    def run(self, result=None):
        """
        Mark --failfast.
        Because if we no rollback following tests will not run obviously.
        """
        if result == None:
            result = self.defaultTestResult( )

        result.failfast = True
        super( TestCase, self ).run( result )