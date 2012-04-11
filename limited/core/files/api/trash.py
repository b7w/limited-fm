# -*- coding: utf-8 -*-

from limited.core import settings
from limited.core.files.utils import FilePath
from limited.core.files.api.base import file_pre_change, FileStorageBaseApi
from limited.core.files.storage import FileNotExist

class FileStorageTrash( FileStorageBaseApi ):
    """
    File Storage additional for operate with trash
    """

    def listdir(self):
        """
        Safe call for list trash files
        """
        if self.fs.exists( settings.LIMITED_TRASH_PATH ) == False:
            self.fs.mkdir( settings.LIMITED_TRASH_PATH )
        return self.fs.listdir( settings.LIMITED_TRASH_PATH, hidden=False )

    def totrash(self, path, signal=True):
        """
        Shortcut for :func:`~limited.core.files.storage.FileStorage.move`
        where second var is :ref:`LIMITED_TRASH_PATH <SETTINGS_TRASH_PATH>`.
        """
        path = self.check( path )
        if signal:
            file_pre_change.send( self, basedir=FilePath.dirname( path ) )
        if self.fs.exists( settings.LIMITED_TRASH_PATH ) == False:
            self.fs.mkdir( settings.LIMITED_TRASH_PATH )
        if self.fs.exists( path ) == False:
            raise FileNotExist( u"'%s' not found" % path )
        self.fs.move( path, settings.LIMITED_TRASH_PATH )