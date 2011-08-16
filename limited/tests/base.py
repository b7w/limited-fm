# -*- coding: utf-8 -*-

from django.test import TestCase

from limited.models import FileLib
from limited.storage import FileStorage, StoragePath


class StorageTestCase( TestCase ):
    """
    Base class if wee need to rollback
    test directory

    It is run always with '--failfast' option

    Best way is to test ``create``, ``mkdir`` and ``clear``
    by your own separately

    To change test data, add them to ``tearDown``
    """
    fixtures = ['dump.json']

    def setUp(self):
        self.path = StoragePath( )
        self.lib = FileLib.objects.get( name="Test" )
        self.storage = FileStorage( self.lib.get_path( ), self.lib.path )

    def tearDown(self):
        try:
            self.storage.clear( u"" )
            self.storage.mkdir( u".TrashBin" )
            self.storage.mkdir( u".TrashBin/Crash Test" )
            self.storage.mkdir( u"Test Folder" )
            self.storage.create( u"content.txt", u"Test line in file" )
            self.storage.create( u"Фото 007.bin", "007" * 2 ** 8 )
        except Exception:
            raise Exception( u"Error happened while rollback changes in 'tearDown'. " +
                "Test Stopped. Clear default data yourself! And test base methods by your own separately" )

    def run(self, result=None):
        """
        Mark --failfast.
        Because if we no rollback following tests will not run obviously.
        """
        if result == None:
            result = self.defaultTestResult( )

        result.failfast = True
        super( TestCase, self ).run( result )