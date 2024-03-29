# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.contrib.auth.models import User

from limited.core.models import FileLib, Home, Permission, Link, History, Profile
from limited.core.management.utils import load_permissions

class InitData:
    """
    Init data for tests. Is is better because of database independence.
    And easier to modify. To load all data call ``LoadAll``.
    """

    def __init__(self):
        self.UserAdmin = None
        self.UserAnon = None
        self.UserB7W = None

        self.LibFM = None
        self.LibTest = None

    def LoadAll(self):
        self.Users( )
        self.Permissions( )
        self.FileLibs( )
        self.Homes( )
        self.Links( )
        self.History( )

    def Users(self):
        self.UserAdmin = User.objects.create_user( 'admin', 'admin@loc.com', 'root' )
        self.UserAdmin.is_staff = True
        self.UserAdmin.is_superuser = True
        self.UserAdmin.save( )
        Profile.objects.filter(user=self.UserAdmin).update(mail_notify=True)

        self.UserAnon = User.objects.create_user( 'Anonymous', 'anon@loc.com' )
        self.UserAnon.save( )

        self.UserB7W = User.objects.create_user( 'B7W', 'b7w@loc.com', 'root' )
        self.UserB7W.save( )
        Profile.objects.filter(user=self.UserB7W).update(mail_notify=True)

    def Permissions(self):
        load_permissions( )

    def FileLibs(self):
        self.LibFM = FileLib( name="FileManager", description="FileManager running files", path="" )
        self.LibFM.save( )

        self.LibTest = FileLib( name="Test", description="FM Test dir", path="tmp/test" )
        self.LibTest.save( )

    def Homes(self):
        perm1 = Permission.objects.get( id=5 )
        Home1 = Home( user=self.UserAnon, lib=self.LibFM, permission=perm1 )
        Home1.save( )

        perm2 = Permission.objects.get( id=37 )
        Home2 = Home( user=self.UserAnon, lib=self.LibTest, permission=perm2 )
        Home2.save( )

        perm3 = Permission.objects.get( id=64 )
        Home3 = Home( user=self.UserB7W, lib=self.LibTest, permission=perm3 )
        Home3.save( )

    def Links(self):
        link = Link( hash="d89d9baa47e8", lib=self.LibTest, path=u"Фото 007.bin" )
        link.expires = datetime.now() + timedelta(days=32)
        link.time = datetime.now()
        link.save( )

    def History(self):
        History1 = History( user=self.UserB7W, lib=self.LibTest, type=2, path=u"Фото 007.bin" )
        History1.time = datetime( 2011, 6, 26, 15, 12, 59 )
        History1.save( )

        History2 = History( user=self.UserAdmin, lib=self.LibTest, type=3, path=u"Фото 070.jpg" )
        History2.time = datetime( 2011, 6, 26, 15, 14, 59 )
        History2.save( )

        History3 = History( user=self.UserAdmin, lib=self.LibTest, type=7, path=u"Фото 007.bin" )
        History3.time = datetime( 2011, 6, 29, 19, 56, 4 )
        History3.extra = "d89d9baa47e8"
        History3.save( )