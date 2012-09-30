# -*- coding: utf-8 -*-
from django.test import TestCase

from limited.core import settings
from limited.core.models import FileLib
from limited.core.tests.data import InitData


class StorageTestCase( TestCase ):
    """
    Base class to init test data in every tests.

    It creates 'test' folder in LIMITED_ROOT_PATH with
    '.TrashBin/Crash Test',
    'Test Folder',
    'content.txt' - Test line in file,
    'Фото 007.bin'

    Class doesn't delete test data!
    It is run always with '--failfast' option
    Best way is to test ``create``, ``mkdir`` and ``clear``
    by your own separately
    """

    def setUp(self):
        self.data = InitData( )
        self.data.LoadAll( )

        self.lib = FileLib.objects.get( name="Test" )
        self.storage = self.lib.getStorage( )

        self.lib2 = FileLib.objects.get( name="FileManager" )
        self.storage2 = self.lib2.getStorage( )

        settings.TEST = True
        settings.LIMITED_ANONYMOUS = False
        settings.LIMITED_ANONYMOUS_ID = self.data.UserAnon.id
        settings.LIMITED_ZIP_HUGE_SIZE = 16 * 1024 ** 2
        settings.LIMITED_FILES_ALLOWED = {'ONLY': [u'^[А-Яа-я\w\.\(\)\+\- ]+$'], 'EXCEPT': [u'.+\.rar', ], }
        settings.LIMITED_SERVE = {
            'BACKEND': 'limited.core.serve.backends.default',
            'INTERNAL_URL': '/protected',
            }

        if self.storage.exists( u"" ):
            self.storage.remove( u"" )
        self.storage.mkdir( u"" )
        self.storage.mkdir( settings.LIMITED_TRASH_PATH )
        self.storage.mkdir( settings.LIMITED_TRASH_PATH + u"/Crash Test" )
        self.storage.mkdir( settings.LIMITED_CACHE_PATH )
        self.storage.mkdir( u"Test Folder" )
        self.storage.extra.create( u"content.txt", u"Test line in file" )
        self.storage.extra.create( u"Фото 007.bin", "007" * 2 ** 8 )

    def run(self, result=None):
        """
        Mark --failfast.
        Because if we no rollback following tests will not run obviously.
        """
        if result == None:
            result = self.defaultTestResult( )

        result.failfast = True
        super( TestCase, self ).run( result )

    def setAnonymous(self, bool):
        """
        Turn ON/OFF ANONYMOUS Open file libs
        """
        settings.LIMITED_ANONYMOUS = bool
